import unittest
from datetime import datetime
from typing import Any, cast

import yaml

from lib.scheduler import MedicationId, ScheduledMedicationsItem, MedicationScheduling, MedicationIntake


class YAMLDatabaseRepository:
    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename

    def read(self) -> dict[MedicationId, ScheduledMedicationsItem]:
        doc: dict[str, Any]
        with open(self._filename, 'r') as file:
            doc = yaml.safe_load(file)
        result: dict[MedicationId, ScheduledMedicationsItem] = {}

        medications_: list[dict[str, Any]] = doc['medications']
        for medication in medications_:
            intakes = [{'when': datetime.fromisoformat(when), 'type': 'PRN'} for when in medication['intakes']]
            schedules = []
            schedule: dict[str, Any]
            for schedule in medication['schedules']:
                schedules.append({'from': datetime.fromisoformat(schedule['from']),
                                  'next': schedule['next'],
                                  'type': schedule['type']})
            current = cast(ScheduledMedicationsItem,
                           {'intakes': intakes, 'schedules': schedules, 'id': medication['id'],
                            'tags': medication['tags']})
            result[MedicationId(medication['id'])] = current
        return result


class YAMLDatabaseRepositoryTest(unittest.TestCase):
    def test_reading_a_sample(self) -> None:
        read = YAMLDatabaseRepository('./database-sample.yml').read()

        datetime_datetime = datetime.fromisoformat('2024-01-05T14:51:00+04')
        expected: dict[MedicationId, ScheduledMedicationsItem] = {
            MedicationId('medication 1'): {
                'intakes': [
                    cast(MedicationIntake, {'type': 'PRN', 'when': datetime_datetime})
                ],
                'schedules': [
                    cast(MedicationScheduling,
                         {'from': datetime.fromisoformat('2024-01-05T14:31:00+04'), 'next': '4 hour', 'type': 'PRN'})
                ],
                'id': MedicationId('medication 1'),
                'tags': ['immediate', 'another tag with spaces']
            },
            MedicationId('medication 2'): {
                'intakes': [
                    cast(MedicationIntake, {'type': 'PRN', 'when': datetime.fromisoformat('2024-01-05T14:51:00+04')}),
                    cast(MedicationIntake, {'type': 'PRN', 'when': datetime.fromisoformat('2024-01-05T14:51:00+03')}),
                ],
                'schedules': [
                    cast(MedicationScheduling,
                         {'from': datetime.fromisoformat('2024-01-05T14:31:00+04'), 'type': 'PRN', 'next': '4 hour'}),
                    cast(MedicationScheduling,
                         {'from': datetime.fromisoformat('2024-01-05T14:31:00+04'), 'type': 'another type',
                          'next': '2 hour'})
                ],
                'id': MedicationId('medication 2'),
                'tags': []
            }
        }

        for id, value in expected.items():
            key: str
            for key in value.keys():
                assert key in ["id", "tags", "intakes", "schedules"]
                self.assertTrue(key in expected[id].keys())
                expected_value = expected[id][key]  # type: ignore
                actual_value = read[id][key]  # type: ignore
                self.assertEqual(expected_value, actual_value,
                                 msg=f'Failure when comparing (id={id}) {key}: {actual_value} vs {expected_value}')
            self.assertEqual(expected[id], read[id], msg=f"Failing for test case {id}")

        self.assertDictEqual(expected, read)
        self.assertEqual(len(expected), len(read))


if __name__ == '__main__':
    unittest.main()
