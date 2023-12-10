from typing import List


def find_overlap(student_schedule: List, teacher_schedule: List) -> List:
    """Сравнивает расписание студента и преподавателя, ищет пересечение со временем, чтобы студент мог подойти"""

    overlaps = []

    for si, s in enumerate(student_schedule):
        sb = s.get('building')  # корпус в котором студент
        sn = s.get('lessonNumberStart')  # номер пары студента
        for ti, t in enumerate(teacher_schedule):
            tb = t.get('building')  # корпус в котором преподаватель
            tn = t.get('lessonNumberStart')  # номер пары преподавателя

            # Если в удалённых корпусах, то студент и преподав. должны быть в нём
            if sb != tb == 'УЛК-12' or tb != sb == 'УЛК-12':
                continue
            if sb != tb == 'УЛК-9' or tb != sb == 'УЛК-9':
                continue
            if sb != tb == 'УЛК-10' or tb != sb == 'УЛК-10':
                continue
            if not (sb == 'УЛК-3' or sb == 'УЛК-4') == (tb == 'УЛК-3' or tb == 'УЛК-4'):
                continue
            if not ((sb == 'УЛК-13' or sb == 'УЛК-14') == (tb == 'УЛК-13' or tb == 'УЛК-14')):
                continue

            # если у студента и у преподавателя пара начинается в одно время, то студент может подойти до пары
            if (si == ti == 0) and (sn == tn):
                overlaps.append(['до начала', s, t])

            # если у студента закачиваются пары раньше преподавателя, то он может подойти после конца своей
            if (si == len(student_schedule) - 1) and (ti != len(student_schedule) - 1) and (tn == sn):
                overlaps.append(['после конца', s, teacher_schedule[ti + 1]])

            # если большая перемена (после чётных пар) и не последняя пара у п-ля, то студент может подойти
            if (sn % 2 == 0) and (ti != len(teacher_schedule) - 1) and (tn == sn + 1):
                overlaps.append(['на перемене между', s, t])

    return overlaps
