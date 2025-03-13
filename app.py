from bobby_bets_agent import ask_bobby, manage_memory, memory_client
import os
import uuid
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

def main():
    print("🏀 Welcome to Bobby Bets NBA Analysis 🏀")
    print("Ask me about any two NBA teams and I'll give you insights!")
    print("Type 'exit' to quit.")
    print("Memory commands: 'clear memory', 'list memory', 'count memory'")
    print()
    
    # Generate a unique user ID or ask for one
    user_id = input("Enter your username (or press Enter for a random ID): ")
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
    print(f"Using user ID: {user_id}")
    print()
    
    while True:
        question = input("Your question: ")
        
        # Check for exit command
        if question.lower() in ['exit', 'quit', 'bye']:
            print("Thanks for using Bobby Bets! Goodbye!")
            break
        
        # Check for memory management commands
        if question.lower() == 'clear memory':
            try:
                memory_client.delete_all(user_id=user_id)
                print(f"\nSuccessfully cleared all memories for user {user_id}.\n")
            except Exception as e:
                print(f"\nError clearing memories: {str(e)}\n")
            continue
        
        if question.lower() == 'list memory':
            try:
                # Try with default format first
                memories = memory_client.get_all(user_id=user_id)
                
                if not memories:
                    print(f"\nNo memories found for user {user_id}.\n")
                    continue
                
                if isinstance(memories, list):
                    memory_list = []
                    for memory in memories:
                        if isinstance(memory, dict) and "memory" in memory:
                            memory_list.append(f"- {memory['memory']}")
                        elif isinstance(memory, dict) and "text" in memory:
                            memory_list.append(f"- {memory['text']}")
                        else:
                            memory_list.append(f"- {str(memory)}")
                    
                    if memory_list:
                        print(f"\nMemories for user {user_id}:\n" + "\n".join(memory_list[:10]) + 
                              (f"\n... and {len(memory_list) - 10} more" if len(memory_list) > 10 else "") + "\n")
                    else:
                        print(f"\nNo readable memories found for user {user_id}.\n")
                else:
                    print(f"\nUnexpected response format: {memories}\n")
            except Exception as e:
                print(f"\nError listing memories: {str(e)}\n")
            continue
        
        if question.lower() == 'count memory':
            try:
                memories = memory_client.get_all(user_id=user_id)
                if isinstance(memories, list):
                    count = len(memories)
                    print(f"\nUser {user_id} has {count} memories stored.\n")
                else:
                    print(f"\nUnexpected response format: {memories}\n")
            except Exception as e:
                print(f"\nError counting memories: {str(e)}\n")
            continue
        
        print("\nAnalyzing... (this may take a moment)")
        try:
            response = ask_bobby(question, user_id=user_id)
            print("\n" + response["output"] + "\n")
        except Exception as e:
            print(f"\nSorry, I encountered an error: {str(e)}\n")

if __name__ == "__main__":
    main() 