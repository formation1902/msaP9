from azure.storage.blob import BlobServiceClient
import os
#
# On recupere les donnes de stockage azure :
#
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container="an-existing-container") 

asa_articles_emb = blob_service_client.get_blob_client("an-existing-container",blob="articles_emb.csv")

articles_emb = asa_articles_emb.download_blob()

print(type(articles_emb))