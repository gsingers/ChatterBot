from chatterbot.adapters.storage import StorageAdapter
from chatterbot.conversation import Statement, Response
import requests


class ChatterBotRestApi(StorageAdapter):

    def __init__(self, **kwargs):
        super(JsonDatabaseAdapter, self).__init__(**kwargs)

        self.api_root = kwargs.get(
            'api_root', 'http://localhost:8000'
        )

    def count(self):
        return len(self._keys())

    def find(self, statement_text):
        values = self.database.data(key=statement_text)

        if not values:
            return None

        return Statement(statement_text, **values)

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements if the response text matches the
        input text.
        """
        for statement in self.filter(in_response_to__contains=statement_text):
            statement.remove_response(statement_text)
            self.update(statement)

        self.database.delete(statement_text)

    def deserialize_responses(self, response_list):
        """
        Takes the list of response items and returns the
        list converted to object versions of the responses.
        """
        in_response_to = []

        for response in response_list:
            text = response["text"]
            del(response["text"])

            in_response_to.append(
                Response(text, **response)
            )

        return in_response_to

    def filter(self, **kwargs):
        """
        Returns a list of statements in the database
        that match the parameters specified.
        """
        results = []

        for key in self._keys():
            values = self.database.data(key=key)

            # Add the text attribute to the values
            values["text"] = key

            if self._all_kwargs_match_values(kwargs, values):

                # Build the objects for the response list
                in_response_to = values["in_response_to"]
                response_list = self.deserialize_responses(in_response_to)
                values["in_response_to"] = response_list

                # Remove the text attribute from the values
                text = values.pop("text")

                results.append(
                    Statement(text, **values)
                )

        return results

    def update(self, statement):
        # Do not alter the database unless writing is enabled
        if not self.read_only:
            data = statement.serialize()

            # Remove the text key from the data
            del(data['text'])
            self.database.data(key=statement.text, value=data)

            # Make sure that an entry for each response exists
            for response_statement in statement.in_response_to:
                response = self.find(response_statement.text)
                if not response:
                    response = Statement(response_statement.text)
                    self.update(response)

        return statement

    def get_random(self):
        from random import choice

        if self.count() < 1:
            raise self.EmptyDatabaseException()

        statement = choice(self._keys())
        return self.find(statement)

    def drop(self):
        """
        Remove the json file database completely.
        """
        import os

        if os.path.exists(self.database.path):
            os.remove(self.database.path)
