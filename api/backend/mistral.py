import os
from pinecone import Pinecone
from mistralai import Mistral

# api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key='2mNBxLl3Be2IA5xjqLqrcjVofjEjfiiY')

#embeddings_batch_response = client.embeddings.create(
#    model=model,
#    inputs=["Embed this sentence.", "As well as this one.", "What ever this is as well"],
#)

pc = Pinecone(api_key='pcsk_6gSjr3_7D8YWJTafc1kBa7ppB1aV8KX16MdoaCTAFtigqHUCVHxb8nRHcqP2awfdsd4jVr')
index = pc.Index('ragtest')

#vector_data = [(str(x), embeddings_batch_response.data[x].embedding) for x in range(len(embeddings_batch_response.data))]

#index.upsert(vector_data)

test_query = "what is as well"
test_embedding = client.embeddings.create(
    model = model,
    inputs = [test_query]
)

responese = index.query(
    vector= test_embedding.data[0].embedding,
    top_k=2,
    include_values=True
)

for i in responese.matches:
    print(i.id)
