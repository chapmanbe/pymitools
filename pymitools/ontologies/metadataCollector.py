"""Includes MetadataCollector class.

Responsible for keeping track of when widget values change or are selected.

"""

import ipywidgets as widgets
from IPython.display import display
import requests


class MetadataCollector:
    """Handle information inside the widgets."""

    def __init__(self, topic, ontologies, required=False, value_changed=None,
                 bioportal_api_key='efa3babf-b23c-4399-89f7-689bb9d576fb'):
        """Provide bioportal key, create widgets.

        Create (but not display) needed widgets. If the topic is required
        before upload, highlight the text box red.

        :param topic: The topic name to be associated with the key words
        :param ontolgies: The ontolgies to be searched.
        :param required: Whether or not the topic is required to have at least
                         one key word added before upload.
        :param value_changed: Callback which is called everytime the first word
                              is added to an empty added words widget or when
                              the last word is removed from the added words
                              widget.
        :param bioportal_api_key: The key used to access the bioportal REST API

        """
        self._topic = topic
        self._required = required
        self._ontologies = ontologies
        self._value_changed = value_changed
        self._color = 'red'
        # self._results_info stores keywords as keys and bioportal
        # results as values
        self._results_info = dict()
        # self._final_results stores only the info for added words
        self._final_results = dict()
        self._selected = None
        self._ready = False

        results_name = topic + " results:"
        self._search_input_widget = widgets.Text(description=topic,
                                                 value='', width='49%')
        self._search_results_widget = widgets.Select(description=results_name,
                                                     options=[],
                                                     width='300')
        self._added_word_widget = widgets.Select(description='selected words:',
                                                 options=[],
                                                 width='300')
        self._add_button = widgets.Button(description='add', width='100%',
                                          disabled=True)
        self._remove_button = widgets.Button(description='remove',
                                             width='100%',
                                             disabled=True)
        if required:
            self._search_input_widget.background_color = self._color

        search_contains = [self._search_input_widget]
        search_container = widgets.HBox(children=search_contains)
        button_contains = [self._add_button, self._remove_button]
        button_container = widgets.VBox(children=button_contains)
        bottom_contains = [self._search_results_widget, button_container,
                           self._added_word_widget]
        bottom_container = widgets.HBox(children=bottom_contains)

        self._container = widgets.VBox(children=[search_container,
                                                 bottom_container])
        self._api_url = 'http://data.bioontology.org/'
        self._key = bioportal_api_key
        self._headers = {'Authorization': 'apikey token=' + self._key}

    def GET(self, url, params=None):
        """Convenient method for requests.get().

        Headers already included in call. JSON response data is returned.

        :param url: The website to access JSON data from.
        :param params: Parameters for the REST request.

        """
        request = requests.get(url, headers=self._headers, params=params)
        return request.json()

    def is_required(self):
        """Return whether the field is required or not before upload."""
        return self._required

    def get_topic(self):
        """Return the topic that is used for the widgets."""
        return self._topic

    def display(self):
        """Display the 5 widgets to be used for the topic(s)."""
        display(self._container)
        self._search_input_widget.observe(self.__search_value_changed,
                                          names='value')
        self._search_results_widget.observe(self.__results_value_change,
                                            names='value')
        self._add_button.on_click(self.__add_button_click)
        self._remove_button.on_click(self.__remove_button_click)
        self._added_word_widget.observe(self.__selected_value_change,
                                        names='value')

    def has_results(self):
        """Check if there are words in the added words widget."""
        return self._ready

    def get_results(self):
        """Return the final dictionary results.

        The dictionary keys are the key words in the added words widget, and
        the values are the responses from bioportal.

        """
        return self._final_results

    def __search(self, search_term, ontologies):
        """Search specified ontologies using bioportals REST API.

        Returns list of suggested keywords and a dictionary with the
        keywords as keys and bioportal response data as values.

        :param searchTerm: The term to search bioportal with.
        :param ontologies: A list of ontology IDs to search.

        """
        parameters = {'ontologies': ontologies,
                      'suggest': 'true', 'pagesize': 15}
        search = self._api_url + 'search?q=' + search_term

        data = self.GET(search, params=parameters)
        nameList = []
        nameDict = {}
        if "collection" in data:
            collection = data["collection"]
        else:
            return (nameList, nameDict)

        for d in collection:
            nameDict[d["prefLabel"]] = d
            nameList.append(d["prefLabel"])

        return (nameList, nameDict)

    def __search_value_changed(self, change):
        new_keyword = change['new'].strip()
        if new_keyword:
            keywords, info = self.__search(new_keyword, self._ontologies)
            if len(keywords) == 0:
                temp = ['NO RESULTS FOUND']
                self._search_results_widget.options = temp
                self._add_button.disabled = True
            else:
                self._search_results_widget.options = keywords
                self._results_info = info
                self._add_button.disabled = False
        else:
            temp = []
            self._search_results_widget.options = temp
            self._selected = None
            self._add_button.disabled = True

    def __results_value_change(self, change):
        self._selected = change['new']

    def __selected_value_change(self, change):
        self._remove_button.disabled = False

    def __add_button_click(self, change):
        tmp = self._selected
        tmp2 = self._added_word_widget.value
        self._final_results[tmp] = self._results_info[tmp]
        added_words = self._added_word_widget.options
        if self._selected not in added_words:
            if (tmp == tmp2):
                self._remove_button.disabled = False
            added_words.append(self._selected)
            self._added_word_widget.options = added_words
            self._ready = True
            # Execute value change delegate
            if self._value_changed:
                self._value_changed()

    def __remove_button_click(self, change):
        selected = self._added_word_widget.value
        added_words = self._added_word_widget.options
        added_words.remove(selected)
        self._added_word_widget.options = added_words
        self._final_results.pop(selected, None)
        if len(self._final_results) == 0:
            self._ready = False
            # Execute value change delegate
            if self._value_changed:
                self._value_changed()
        self._remove_button.disabled = True
