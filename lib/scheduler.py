from datetime import datetime, timedelta
from typing import Any, Dict, TypedDict


class MedicationId:
    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        return self._value

    def __eq__(self, __value: Any) -> Any:
        return self._value == __value

    def __hash__(self) -> int:
        return self._value.__hash__()


MedicationSchedulingItem = TypedDict('MedicationSchedulingItem', {'from': datetime,
                                                                  'next': str,
                                                                  'type': str})


class MedicationScheduling:
    def __init__(self, id: MedicationId, tags: Any, scheduling: MedicationSchedulingItem):
        super().__init__()
        self._id = id
        self._tags = tags
        self._scheduling = scheduling


MedicationIntakeItem = TypedDict('MedicationIntakeItem', {'when': datetime,
                                                          'type': str})


class MedicationIntake:
    def __init__(self, id: MedicationId, bag: MedicationIntakeItem):
        self._id = id
        self._bag = bag


ScheduledMedicationItem = TypedDict('ScheduledMedicationItem', {'when': datetime, 'type': str})


class ScheduledMedication:
    def __init__(self, id: MedicationId, bag: ScheduledMedicationItem):
        self._id = id
        self._bag = bag

    def __eq__(self, __value: Any) -> Any:
        return self._id == __value._id and self._bag == __value._bag


ScheduledMedicationsXX = TypedDict('ScheduledMedicationsXX',
                                   {'intakes': list[MedicationIntake], 'schedules': list[MedicationScheduling]})


class Scheduler:
    _scheduled_medicines: dict[MedicationId, ScheduledMedicationsXX]

    def __init__(self) -> None:
        self._scheduled_medicines = {}

    def next_medicine_by_id(self, id: MedicationId) -> ScheduledMedication:
        assert id in self._scheduled_medicines.keys()
        medicine_with_id = self._scheduled_medicines[id]
        last_schedule = medicine_with_id['schedules'][-1]
        date_delta = self._parse_time_delta_for_schedule(last_schedule)
        next_intake_from_last_intake = self._xz(date_delta, medicine_with_id)
        next_intake_from_scheduling = self._xy(date_delta, last_schedule)
        intake = max(next_intake_from_last_intake, next_intake_from_scheduling)
        return ScheduledMedication(last_schedule._id,
                                   {'when': intake, 'type': last_schedule._scheduling['type']})

    def _xz(self, date_delta: timedelta, medicine_with_id: ScheduledMedicationsXX) -> datetime:
        last_intake_date = self._next_intake_datetime(medicine_with_id)
        next_intake_from_last_intake = last_intake_date + date_delta
        return next_intake_from_last_intake

    def _xy(self, date_delta: timedelta, last_schedule: MedicationScheduling) -> datetime:
        last_schedule_date: datetime = last_schedule._scheduling['from']
        next_intake_from_scheduling = last_schedule_date + date_delta
        return next_intake_from_scheduling

    def _next_intake_datetime(self, scheduled_medication: ScheduledMedicationsXX) -> datetime:
        return scheduled_medication['intakes'][-1]._bag['when']

    def add_medicine(self, medication_scheduling: MedicationScheduling) -> None:
        scheduling__id = medication_scheduling._id
        if scheduling__id not in self._scheduled_medicines:
            self._scheduled_medicines[scheduling__id] = {'intakes': [], 'schedules': []}
        self._scheduled_medicines[scheduling__id]['schedules'].append(medication_scheduling)

    def register_intake(self, intake: MedicationIntake) -> None:
        assert intake._id in self._scheduled_medicines.keys(), f"The intake '{intake._id}' does not correspond to any registered medication. Currently: {list(self._scheduled_medicines.keys())}, len={len(self._scheduled_medicines)}"
        self._scheduled_medicines[intake._id]['intakes'].append(intake)

    def _parse_time_delta_for_schedule(self, last_schedule: MedicationScheduling) -> timedelta:
        return self._parse_time_delta(last_schedule._scheduling['next'])

    @staticmethod
    def _parse_time_delta(text_description: str) -> timedelta:
        if 'hour' in text_description:
            text_description = text_description.replace('hour', '').strip()
            return timedelta(hours=int(text_description))
        else:
            assert False, 'Invalid/Unsupported time delta format: {}'.format(text_description)
