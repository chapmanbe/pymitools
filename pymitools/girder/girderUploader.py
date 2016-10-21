"""Includes girderUploader class.

girderUploader uses the girder client to upload an item
or a folder to girder.

"""

import girder_client
import os


class GirderUploader(object):
    """Use girder client to upload files to girder.

    Option to request metadata from the user before upload,
    can be uploaded without metadata as well.

    """

    def __init__(self, girder_api_url, username, password):
        """Autheticate with girder instance, prepare for interaction.

        param: girder_api_url: the url to the girder instance.
        param: username: the user name of the owner of the specific instance
        param: password: the password for the user name.

        """
        self._client = girder_client.GirderClient(apiUrl=girder_api_url)
        self._client.authenticate(username, password)
        self._metadata = dict()
        self._local_path = None
        self._isfolder = False
        self._girder_dest_path = None
        self._client.add_folder_upload_callback(self.__upload_folder_callback)
        self._client.add_item_upload_callback(self.__upload_item_callback)


    def upload_file_with_metadata(self, girder_dest_path, local_path, metadata):
        """Upload folder to girder with associated metadata.

        :param girder_dest_path: Unix style path to destination on girder.
        :param local_path: Path to file/folder to upload.
        :param metadata: metadata preset

        """
        self._metadata = metadata
        self._local_path = local_path
        self._girder_dest_path = girder_dest_path
        parentId, parentType = self.__get_parent_id_and_type()
        self._client.upload(self._local_path, parentId,
                            parent_type=parentType,
                            leaf_folders_as_items=True)

    def upload_folder_with_metadata(self, girder_dest_path, local_path, metadata):
        """Upload folder to girder with associated metadata.

        :param girder_dest_path: Unix style path to destination on girder.
        :param local_path: Path to file/folder to upload.
        :param metadata: metadata preset

        """
        self._metadata = metadata
        self._local_path = local_path
        self._girder_dest_path = girder_dest_path
        parentId, parentType = self.__get_parent_id_and_type()
        self._client.upload(self._local_path, parentId,
                            parent_type=parentType,
                            leaf_folders_as_items=True)

    def upload_folder(self, girder_dest_path, local_path):
        """Begin the upload process.

        If metadata is required, input forms are created and displayed, and
        metadata input is collected before upload begins.

        :param girder_dest_path: Unix style path to destination on girder.
        :param local_path: Path to folder to upload.

        """
        self._local_path = local_path
        self._isfolder = True
        self._girder_dest_path = girder_dest_path
        parentId, parentType = self.__get_parent_id_and_type()
        self.__upload(self._local_path, parentId, parent_type=parentType)

    def upload_file(self, girder_dest_path, local_path):
        """Begin the upload process.

        If metadata is required, input forms are created and displayed, and
        metadata input is collected before upload begins.

        :param girder_dest_path: Unix style path to destination on girder.
        :param local_path: Path to file to upload.

        """
        self._local_path = local_path
        self._isfolder = False
        self._girder_dest_path = girder_dest_path
        parentId, parentType = self.__get_parent_id_and_type()
        self.__upload(self._local_path, parentId, parentType)


    def __upload(self, local_path, parent_id, parent_type):
        if self._isfolder:
            self._client.upload(local_path, parent_id, parent_type=parent_type,
                                leaf_folders_as_items=True)
        else:
            self._client.upload(local_path, parent_id, parent_type=parent_type,
                                leaf_folders_as_items=True)

    def __submit_callback(self, results):
        parentId, parentType = self.__get_parent_id_and_type()

        def get_id(id_url):
            temp_id = id_url.rsplit('/',  1)[-1]
            if '#' in temp_id:
                # RADLEX
                id = temp_id.rsplit('#', 1)[-1]
                return id[3:]
            else:
                # DOID, UBERON
                return temp_id.rsplit('_', 1)[-1]

        def extract_info(topic):
            keyword_dict = results[topic]
            for keyword in keyword_dict:
                dictionary = keyword_dict[keyword]
                ontology_url = dictionary['links']['ontology']
                json_result = self._bio_search.GET(ontology_url)
                acronym = json_result['acronym']
                name = json_result['name']
                resource = dictionary['@id']
                id = get_id(resource)

                meta = {'Ontology Name': name,
                        'Ontology Acronym': acronym,
                        'Name': keyword,
                        'ID': id,
                        'Resource URL': resource}
                self._metadata[topic].append(meta)

        for topic in results:
            self._metadata[topic] = []
            extract_info(topic)

        self.__upload(self._local_path, parentId, parentType)

    def __get_parent_id_and_type(self):
        params = {'path': self._girder_dest_path, 'test': True}
        response = self._client.get('resource/lookup',
                                    parameters=params)
        parentType = response['_modelType']
        parentId = response['_id']
        return (parentId, parentType)

    def __upload_item_callback(self, item, filepath):
        self._client.addMetadataToItem(item['_id'], self._metadata)

    def __upload_folder_callback(self, folder, filepath):
        self._client.addMetadataToFolder(folder['_id'], self._metadata)
