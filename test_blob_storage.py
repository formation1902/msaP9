import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# os.environ['AZURE_USERNAME'] = 'mouhcine.sahbani@yahoo.fr'
# os.environ['AZURE_PASSWORD'] = 'Naw.1902'
# os.environ['AZURE_CLIENT_ID']     = 'b1e27bcf-9136-49b9-9746-1a7550e38fb0'
# os.environ['AZURE_TENANT_ID']     = '592be489-32f2-4ead-9496-bffb9b5ba379'
# os.environ['AZURE_CLIENT_SECRET'] = 'noW8Q~rz0OmddFZwKoHdRJpDib_BZA.H_bII5bsw'

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
print(connect_str)
try:
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container="an-existing-container") 
    
    print("\nListing blobs...")
    # List the blobs in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)
        
    download_file_path = "./mon_fichier_from_storageaccount_cbrs_users_referentiel.pck" 
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob('cbrs_users_referentiel.pck').readall())
        
    download_file_path = "./mon_fichier_from_storageaccount_elected_categories.pck" 
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob('elected_categories.pck').readall())
        
except Exception as ex:
    print('Exception:')
    print(ex)
    
    
   