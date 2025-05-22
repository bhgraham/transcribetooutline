from typing import NamedTuple, List, Union

class Timestamp(NamedTuple):
    start: str
    end: str

class Transcript(NamedTuple):
    title: str
    content: str
    timestamps: List[Timestamp]

class ClassType(str):
    LECTURE = "Lecture"
    SEMINAR = "Seminar"
    WORKSHOP = "Workshop"