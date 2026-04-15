from agent.core import ProjectAgent

if __name__ == '__main__':
  agent=ProjectAgent()
  while True:
    user_input=input("project management system is running, enter your message:,enter 'quit' to exit: ")
    if user_input.lower()=='quit':
      break
    response=agent.run(user_input)
    print(f"project management system: {response}")