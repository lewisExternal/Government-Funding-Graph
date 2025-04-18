"""Unit tests for the ukri_utils module."""
import unittest
import sys
import os
import networkx as nx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.ukri_utils # pylint: disable=consider-using-from-import, import-error, wrong-import-position

class Testing(unittest.TestCase):
    "Testing class for ukri_utils related tests"

    def test_parse_data(self):
        "Example parsing of project data"
        example_data = [{
            "projectComposition": {
                "project": {
                    "id": "1E034EEF-F749-4E8B-B736-A5B2B7115C23",
                    "resourceUrl": "http://gtr.ukri.org/api/projects?ref=160004",
                    "title": "(NOW 160051) High Value Manufacturing Technology Innovation Centre - Project Funding",
                    "status": None,
                    "grantReference": "160004",
                    "grantCategory": "Centres",
                    "abstractText": None,
                    "potentialImpactText": None,
                    "fund": {
                        "valuePounds": 176250001,
                        "start": 1317423600000,
                        "end": 1459378800000,
                        "funder": {
                            "id": "E18E2F0F-AC7D-4E02-9559-669F7C8FEC74",
                            "resourceUrl": "http://gtr.ukri.org/api/organisation/E18E2F0F-AC7D-4E02-9559-669F7C8FEC74",
                            "name": "Innovate UK"
                        },
                        "type": "INCOME_ACTUAL"
                    },
                    "output": None,
                    "publications": None,
                    "identifiers": None,
                    "technicalSummary": None,
                    "projectHierarchy": None,
                    "studentshipHierarchy": None,
                    "healthCategories": [],
                    "researchActivities": [],
                    "researchSubjects": [],
                    "researchTopics": [],
                    "rcukProgrammes": [],
                    "hasClassifications": False
                },
                "leadResearchOrganisation": {
                    "id": "2748CFA3-A2A3-46E1-B482-DAE72A6CB0FA",
                    "resourceUrl": "http://gtr.ukri.org/api/organisation/2748CFA3-A2A3-46E1-B482-DAE72A6CB0FA",
                    "name": "HIGH VALUE MANUFACTURING CATAPULT",
                    "website": None,
                    "address": None,
                    "department": None,
                    "typeInd": None,
                    "federatedIds": None
                },
                "personRoles": [
                    {
                        "id": "A936E693-EBA6-46C8-821B-D0E1EE425018",
                        "resourceUrl": "http://gtr.ukri.org/api/person/A936E693-EBA6-46C8-821B-D0E1EE425018",
                        "firstName": "Research",
                        "otherNames": None,
                        "surname": "Finance",
                        "email": None,
                        "orcidId": None,
                        "roles": [
                            {
                                "name": "PRINCIPAL_INVESTIGATOR",
                                "start": None,
                                "end": None
                            }
                        ],
                        "principalInvestigator": True,
                        "coInvestigator": False,
                        "fellow": False,
                        "projectManager": False,
                        "researcher": False,
                        "researcherCOI": False,
                        "trainingGrantHolder": False,
                        "supervisor": False,
                        "student": False,
                        "displayName": "Finance, Research",
                        "fullName": "Research Finance"
                    }
                ],
                "collaborations": None,
                "organisationRoles": None,
                "principalInvestigators": [
                    {
                        "id": "A936E693-EBA6-46C8-821B-D0E1EE425018",
                        "resourceUrl": "http://gtr.ukri.org/api/person/A936E693-EBA6-46C8-821B-D0E1EE425018",
                        "firstName": "Research",
                        "otherNames": None,
                        "surname": "Finance",
                        "email": None,
                        "orcidId": None,
                        "roles": [
                            {
                                "name": "PRINCIPAL_INVESTIGATOR",
                                "start": None,
                                "end": None
                            }
                        ],
                        "principalInvestigator": True,
                        "coInvestigator": False,
                        "fellow": False,
                        "projectManager": False,
                        "researcher": False,
                        "researcherCOI": False,
                        "trainingGrantHolder": False,
                        "supervisor": False,
                        "student": False,
                        "displayName": "Finance, Research",
                        "fullName": "Research Finance"
                    }
                ],
                "coInvestigators": [],
                "fellows": [],
                "projectManagers": [],
                "researchers": [],
                "researcherCOIs": [],
                "supervisors": [],
                "students": [],
                "trainingGrantHolders": []
            },
            "abstractSnippet": None
        }
        ]
        result = utils.ukri_utils.parse_data(example_data)
        expected = [
            {
                'funder_name': 'Innovate UK',
                'funder_link': 'http://gtr.ukri.org/api/organisation/E18E2F0F-AC7D-4E02-9559-669F7C8FEC74',
                'project_title': '(NOW 160051) High Value Manufacturing Technology Innovation Centre - Project Funding',
                'project_grant_reference': '160004',
                'value': 176250001,
                'lead_research_organisation': 'HIGH VALUE MANUFACTURING CATAPULT',
                'lead_research_organisation_link': 'http://gtr.ukri.org/api/organisation/2748CFA3-A2A3-46E1-B482-DAE72A6CB0FA',
                'people': [
                    {
                        'id': 'A936E693-EBA6-46C8-821B-D0E1EE425018',
                        'resourceUrl': 'http://gtr.ukri.org/api/person/A936E693-EBA6-46C8-821B-D0E1EE425018',
                        'firstName': 'Research',
                        'otherNames': None,
                        'surname': 'Finance',
                        'email': None,
                        'orcidId': None,
                        'roles': [{'name': 'PRINCIPAL_INVESTIGATOR', 'start': None, 'end': None}],
                        'principalInvestigator': True,
                        'coInvestigator': False,
                        'fellow': False,
                        'projectManager': False,
                        'researcher': False,
                        'researcherCOI': False,
                        'trainingGrantHolder': False,
                        'supervisor': False,
                        'student': False,
                        'displayName': 'Finance, Research',
                        'fullName': 'Research Finance'
                    }
                ],
                'project_url': 'http://gtr.ukri.org/api/projects?ref=160004'
            }
        ]
        self.assertEqual(result, expected)


    def test_annotate_value_on_graph(self):
        "Test that funding sizes are normalized"
        result, expected = True, False
        graph = nx.DiGraph()
        graph.add_node(
            "Test funder 1", title="Test funder 1", group="funder_name", size=100, funding = 100
        )
        graph.add_node(
            "Test funder 2", title="Test funder 2", group="funder_name", size=100, funding = 200
        )
        graph.add_node(
            "Test lead research organisation 1", title="Test lead research organisation 2", group="lead_research_organisation", size=100, funding = 100
        )
        graph.add_node(
            "Test lead research organisation 2", title="Test lead research organisation 2", group="lead_research_organisation", size=100, funding = 100
        )
        utils.ukri_utils.annotate_value_on_graph(graph)
        result = [data for _, data in graph.nodes(data=True)]
        expected = [{'title': 'Test funder 1 | £ 100 |  34 %', 'group': 'funder_name', 'size': 340, 'funding': 100}
                    ,{'title': 'Test funder 2 | £ 200 |  67 %', 'group': 'funder_name', 'size': 670, 'funding': 200}
                    ,{'title': 'Test lead research organisation 2 | £ 100 |  50 %', 'group': 'lead_research_organisation', 'size': 500, 'funding': 100}
                    ,{'title': 'Test lead research organisation 2 | £ 100 |  50 %', 'group': 'lead_research_organisation', 'size': 500, 'funding': 100}]
        self.assertEqual(sorted([str(item) for item in result]), sorted([str(item) for item in expected]))

if __name__ == "__main__":
    unittest.main()
