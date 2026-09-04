
import asyncio
from langgraph.types import interrupt, Command
from .get_receipt import find_next_available_appointment, format_appointment_confirmation


async def book_appointment(state):
    print("NODE: book_appointment")

        
    # -----------------------------------------------------------------
    # INTERRUPT: Human reviews candidate doctors before booking
    # -----------------------------------------------------------------
    interrupt_data = state['before_interrupt']

    
    # INTERRUPT! Execution pauses here
    human_response = interrupt(interrupt_data)
    
    # When resumed, human_response contains the human's decision
    print(f"\n👤 Human response received: {human_response}")
    

    if human_response["action"] == "select_doctor":
        
        
        for doctor in interrupt_data['candidate_doctors']:
            if doctor['id'] == int(human_response["doctor_id"]):
                appointment = find_next_available_appointment(doctor)
                
        
                confirmation = format_appointment_confirmation(
                    doctor=doctor,
                    appointment_time=appointment,
                    patient_name=state['patient_info']['name'],
                )

                print(confirmation)
                print("====================================================")
                
    
        return {"confirmation": confirmation}
    elif human_response["action"] == "modify_criteria":
        pass # for now

    else: 
        pass





if __name__ == "__main__":
    asyncio.run(book_appointment({}))