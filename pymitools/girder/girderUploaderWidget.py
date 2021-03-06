"""Includes girderUploader class.

girderUploader uses the girder client to upload an item
or a folder to girder.

"""

import girder_client
import os
from bioportalSearchWidgets import BioportalSearchWidgets
from .girderUploader import GirderUploader

class GirderUploaderWidget(GirderUploader):
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

        super(GirderUploaderWidget, self).__init__(girder_api_url, username, password)
        self._bio_search = BioportalSearchWidgets(self.__submit_callback)
        self._client.add_folder_upload_callback(self.__upload_folder_callback)
        self._client.add_item_upload_callback(self.__upload_item_callback)


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
        if self._request_metadata:
            self._bio_search.display_widgets()
        else:
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
        if self._request_metadata:
            self._bio_search.display_widgets()
        else:
            parentId, parentType = self.__get_parent_id_and_type()
            self.__upload(self._local_path, parentId, parentType)

    def request_metadata(self, topic, ontologies, require=False):
        """Create field to request metadata from the user.

        Create metadata request form. The form is displayed when the
        upload for the file/folder begins. e,g, upload_folder()

        Prior to uploading the file/folder to girder, metadata may be
        requested from the user. Given the provided ontology, the user
        searches the ontologies for keywords.

        :param topic:       Topic of the metadata, what it's requested to
                            describe (e.i., region, disease).
        :param ontologies:  List of ontology IDs to be searched.
        :param require:     Whethere or not to require this metadata to be
                            filled before upload.

        """
        self._request_metadata = True
        self._bio_search.add_search_widget(topic, ontologies, require)


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

        self._GirderUploader__upload(self._local_path, parentId, parentType)

