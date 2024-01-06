import unittest
from datetime import datetime

from lib.scheduler import Scheduler, MedicationScheduling, ScheduledMedication, MedicationId, MedicationIntake


class SchedulerTest(unittest.TestCase):
    MEDICATION_NAME = 'Inmediate 1'

    def setUp(self) -> None:
        self.scheduler = Scheduler({})

    def test_the_intake_matches_the_schedule_perfectly(self) -> None:
        same_date = '2024-01-05T11:38:00+04'
        self.scheduler.add_medicine(self._create_medicine_scheduling(self.MEDICATION_NAME, same_date))
        self.scheduler.register_intake(self._create_intake(self.MEDICATION_NAME, same_date))

        actual = self.scheduler.next_medicine_by_id(MedicationId(self.MEDICATION_NAME))

        self.assertEqual(self._create_scheduled_medicine(self.MEDICATION_NAME, '2024-01-05T15:38:00+04'), actual)

    def test_the_intake_is_after_the_schedule_with_a_single_intake__should_plan_the_scheduling_after_the_last_intake(
            self) -> None:
        self.scheduler.add_medicine(self._create_medicine_scheduling(self.MEDICATION_NAME, '2024-01-05T11:38:00+04'))
        self.scheduler.register_intake(self._create_intake(self.MEDICATION_NAME, '2024-01-05T12:38:00+04'))

        actual = self.scheduler.next_medicine_by_id(MedicationId(self.MEDICATION_NAME))

        self.assertEqual(self._create_scheduled_medicine(self.MEDICATION_NAME, '2024-01-05T16:38:00+04'), actual)

    def test_the_intake_is_after_the_schedule_with_multiple_intakes__should_plan_the_scheduling_after_the_last_intake(
            self) -> None:
        self.scheduler.add_medicine(self._create_medicine_scheduling(self.MEDICATION_NAME, '2024-01-05T11:38:00+04'))
        self.scheduler.register_intake(self._create_intake(self.MEDICATION_NAME, '2024-01-05T12:38:00+04'))
        self.scheduler.register_intake(self._create_intake(self.MEDICATION_NAME, '2024-01-06T12:38:00+04'))

        actual = self.scheduler.next_medicine_by_id(MedicationId(self.MEDICATION_NAME))

        self.assertEqual(self._create_scheduled_medicine(self.MEDICATION_NAME, '2024-01-06T16:38:00+04'), actual)

    def test_the_last_intake_is_before_the_schedule__should_plan_the_scheduling_after_the_initial_scheduling(
            self) -> None:
        self.scheduler.add_medicine(self._create_medicine_scheduling(self.MEDICATION_NAME, '2024-01-05T11:38:00+04'))
        self.scheduler.register_intake(self._create_intake(self.MEDICATION_NAME, '2024-01-05T10:38:00+04'))

        actual = self.scheduler.next_medicine_by_id(MedicationId(self.MEDICATION_NAME))

        self.assertEqual(self._create_scheduled_medicine(self.MEDICATION_NAME, '2024-01-05T15:38:00+04'), actual)

    def _create_medicine_scheduling(self, id: str, from_: str) -> MedicationScheduling:
        return MedicationScheduling(MedicationId(id), ['immediate'],
                                    {'from': datetime.fromisoformat(from_),
                                     'next': '4 hour',
                                     'type': 'PRN'})

    def _create_intake(self, id: str, from_: str) -> MedicationIntake:
        return MedicationIntake(MedicationId(id),
                                {'when': datetime.fromisoformat(from_), 'type': 'PRN'})

    def _create_scheduled_medicine(self, id: str, date_: str) -> ScheduledMedication:
        return ScheduledMedication(MedicationId(id),
                                   {'when': datetime.fromisoformat(date_), 'type': 'PRN'})


if __name__ == '__main__':
    unittest.main()
