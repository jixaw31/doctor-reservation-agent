



async def decide_gather_user_info(state):
    
    print(state["patient_info"])
    if state["patient_info"]["city"] != None and state["patient_info"]["name"] != None and state["patient_info"]["phone_number"] != None:
        return "decide_route"
    else:
        return "ask_user_info"

if __name__ == "__main__":
    pass