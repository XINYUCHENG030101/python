from langchain_ollama import ChatOllama

ollama_model = ChatOllama(model="deepseek-r1:1.5b", base_url="http://127.0.0.1:11434")
print(ollama_model.invoke("你是谁？").content)
