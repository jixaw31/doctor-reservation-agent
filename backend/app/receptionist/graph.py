from langgraph.graph import StateGraph, START
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import os, asyncio
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langgraph.types import Command

from .schemas import MyMessagesState
from .nodes.call_model.main import call_model
from .nodes.decide_route.main import decide_route, classifier
from .nodes.call_casual_model.main import call_casual_model
from .nodes.helper_nodes import *
from .nodes.query_converter.main import convert_query
from .nodes.book_appointment.main import book_appointment
from .nodes.search.main import search
from .nodes.rerank.main import rerank
from .nodes.ask_user_info.main import ask_user_info
from .nodes.decide_search_doctor.main import decide_search_doctor
from .nodes.decide_gather_user_info.main import decide_gather_user_info
from .nodes.gather_user_info.main import gather_user_info


async def create_graph(checkpointer):

    builder = StateGraph(MyMessagesState)

    builder.add_node(call_model)
    builder.add_node(call_casual_model)
    builder.add_node(decide_route)
    builder.add_node(hardcoded_response)
    builder.add_node(book_appointment)
    builder.add_node(remove_redundant_response)
    builder.add_node(convert_query)
    builder.add_node(search)
    builder.add_node(rerank)
    builder.add_node(ask_user_info)
    builder.add_node(decide_search_doctor)
    builder.add_node(gather_user_info)
    

    builder.add_edge(START, "decide_route") 
    
    builder.add_conditional_edges(
        "decide_route",
        classifier,
        {
            "casual": "call_casual_model",
            "looking_for_doctor": "gather_user_info",
        }
    )
    
    builder.add_conditional_edges(
        "gather_user_info",
        decide_gather_user_info,
        {
            "ask_user_info": "ask_user_info", # 
            "decide_route": "convert_query",
        }
    )
    
    builder.add_edge("convert_query", "search") 
    builder.add_edge("search", "rerank") 
    builder.add_edge("rerank", "book_appointment")
  


    builder.add_edge("call_casual_model", "remove_redundant_response") 

    graph = builder.compile(
        checkpointer=checkpointer,
    )
    
    return graph



load_dotenv('.env')

collection_name = "847f5e78-25b0-46b0-8188-1ebefd9c2772"
config = {"configurable": {"thread_id": collection_name}}



human_inputs_1 = ["سلام، وقتتون بخیر", "برای مادرم دنبال دکتر مغز اعصاب هستم", "ما در مشهد زندگی می کنیم و اسم او نیلوفر رضایی است."]

human_inputs_2 = ["سلام، وقت بخیر. پسرم یه حساسیت پوستی شدید گرفته. یه نوبت برای دکتر می‌خوام.", "به نام علی رضایی، پسرم ۷ سالشه.", "شماره تماس: ۰۹۳۵۹۸۷۶۵۴۳", "اصفهان"]

human_inputs_3 = ["سلام، وقتتون بخیر. من سه روزه درد شدید دندان دارم و صورت‌م متورم شده. هر دکتری که زنگ می‌زنم می‌گه تعطیله. لطفاً یه دکتر دندانپزشک اورژانسی پیدا کنید هرچه سریعتر.",
                  "اسم بیمار علی عباسی است.",
                  "بله. شماره من ۰۳۱-۳۳۵۵-۴۴۸۸ و در نزدیکی تهران سکونت دارم."]

human_inputs_4 = []


async def main():
    
    async with AsyncRedisSaver.from_conn_string(
        os.getenv("REDIS_URI"), 
        ttl={"default_ttl": 3600, "refresh_on_read": True}
    ) as redis_cp:
        
        graph = await create_graph(redis_cp) # Must go to container. maybe create a service out of it.

        
        for m in human_inputs_3:
            result = await graph.ainvoke({
                "messages": [HumanMessage(content=m)],
                "resource_collection_name": collection_name,
                "confirmation": "",
            },
            config=config,
            stream_mode="values",
            )
            

            if "__interrupt__" in result:
                interrupts = result["__interrupt__"]

                for interrupt_item in interrupts:
                    for doctor in interrupt_item.value['candidate_doctors']:
                        print(doctor)

        
        res_input = input("Choose select_doctor or cancel_booking")
        if res_input == "select_doctor":
            doctor_id = input("enter doctor's id to proceed.")

        human_response = {
            "action": res_input,
            "doctor_id": doctor_id,
        }        

        result = await graph.ainvoke(
            Command(resume=human_response),
            config=config,
        )

        print(result)
            
    
if __name__ == "__main__":

    asyncio.run(main())