"""
This module contains the class to manage timestamps
"""
# For type annotation
from __future__ import annotations   
# from typing import Union

import copy
import random


class ObsTime:
    """
    Class to represent the phenomenom time of an observation.
    """

    BASE_YEAR = 2000
    UNIX_BASE_YEAR = 1970
	
    ROUND_TO_SEC = 1

    __READ_FMT = "2D/2M/4Y 2h:2m:2s"
    __PRINT_FMT = "2D/2M/4Y 2h:2m:2s"
    __PRECOMPILED_READ_FMT = [
        ("2D", 0),
        ("2M", 3),
        ("4Y", 6),
        ("2h", 11),
        ("2m", 14),
        ("2s", 17),
    ]

    __fmt_nd = ["{:01d}", "{:02d}", "{:03d}", "{:04d}"]
    __codes = [
        "1D", "2D",
        "1M", "2M",
        "2Y", "4Y",
        "1h", "2h",
        "1m", "2m",
        "1s", "2s",
        "1z", "2z", "3z",
    ]

    __day_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    __month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    __day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    __day_of_base_date = 3  # Thu 01/01/1970
    

    def __init__(self, year: int = 1970, month: int = 1, day: int = 1, hour: int = 0, min: int = 0, sec: int = 0, ms: int = 0, zone: int = 0):
        """__init__ Constructor of :class:`ObsTime` class

        Default value : 01/01/1970 00:00:00.000

        :param year: Year, defaults to 1970
        :param month: month defaults to 1
        :param day: day of month, defaults to 1
        :param hour: your, defaults to 0
        :param min: minute, defaults to 0
        :param sec: second, defaults to 0
        :param ms: millisecond, defaults to 0
        :param zone: time zone, defaults to 0
        """

        if isinstance(year, str):

            time = ObsTime.readTimestamp(year)
            self.day = time.day
            self.month = time.month
            self.year = time.year
            self.hour = time.hour
            self.min = time.min
            self.sec = time.sec
            self.ms = time.ms
            self.zone = zone

        else:

            self.day = day
            self.month = month
            self.year = year
            self.hour = hour
            self.min = min
            self.sec = sec
            self.ms = ms
            self.zone = zone

    def copy(self) -> ObsTime:   
        """Copy the object

        :return: copy of current object
        """
        return copy.deepcopy(self)

    @staticmethod
    def setPrintFormat(format: str):   
        """Set the format for printing a ObsTime object

        The print format is use by the :func:`ObsTime.__str__` method

        :param format: Format for printing ObsTime
        """
        ObsTime.__PRINT_FMT = format

    @staticmethod
    def setReadFormat(format: str):   
        """Set the format for reading a ObsTime object

        :param format: Format for reading
        """
        ObsTime.__READ_FMT = format
        ObsTime.__PRECOMPILED_READ_FMT = ObsTime.__precompileReadFmt(ObsTime.__READ_FMT)

    @staticmethod
    def getPrintFormat() -> str:   
        """Return the print format

        :return: The print format
        """
        return ObsTime.__PRINT_FMT

    @staticmethod
    def getReadFormat() -> str:   
        """Return the read format

        :return: The read format
        """
        return ObsTime.__READ_FMT
      
    @staticmethod  
    def isLeapYear(year) -> bool:
        return ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)))

    @staticmethod
    def readUnixTime(elapsed_seconds: float) -> ObsTime:   
        """Converting elapsed float seconds since 01/01/1970 in ObsTime

        **Warning:** does not consider leap seconds (31 since 1970)

        :param elapsed_seconds: Elapsed seconds
        :return: Coverted time
        """
        '''
        # elapsed is in second or in millisecond ?
        from datetime import datetime
        from calendar import timegm
        nowobj = datetime.now()
        t = datetime(nowobj.year, nowobj.month, nowobj.day, 0, 0, 0)
        tps = timegm(t.timetuple())
        if elapsed_seconds > tps:
            elapsed_seconds = elapsed_seconds / 1000
        '''

        time = ObsTime()

        SECOND_PER_YEAR = 86400 * 365
        # SECOND_PER_MONTH = 86400 * 28

        # Year
        sec = 0
        year = ObsTime.UNIX_BASE_YEAR
        while sec < elapsed_seconds - SECOND_PER_YEAR:
            sec += SECOND_PER_YEAR
            if ObsTime.isLeapYear(year):
                sec += 86400
            year += 1
        time.year = year
        elapsed_seconds -= sec

        # Month
        month = 0
        for i in range(12):
            sec_on_month = ObsTime.__day_per_month[month] * 86400
            #if (month == 1) and (year % 4 == 0):
            if (month == 1) and ObsTime.isLeapYear(year):
                sec_on_month += 86400
            if elapsed_seconds < sec_on_month:
                break
            elapsed_seconds -= sec_on_month
            month += 1

        time.month = month + 1

        # Day
        time.day = (int)(elapsed_seconds / 86400) + 1
        elapsed_seconds -= (time.day - 1) * 86400

        # Hour
        time.hour = (int)(elapsed_seconds / 3600)
        elapsed_seconds -= time.hour * 3600

        # Minute
        time.min = (int)(elapsed_seconds / 60)
        elapsed_seconds -= time.min * 60

        # Second
        time.sec = (int)(elapsed_seconds)
        elapsed_seconds -= time.sec

        # Milisecond
        time.ms = (int)(elapsed_seconds * 1000)

        return time

    def toAbsTime(self) -> float:   
        """Converting to elapsed float seconds since 01/01/1970 (or 01/01/UNIX_BASE_YEAR)

        **Warning:** does not consider leap seconds since 1972

        :return: elapsed float seconds
        """
        seconds = 0
        for y in range(ObsTime.UNIX_BASE_YEAR, self.year):
            seconds += 86400 * 365
            if ObsTime.isLeapYear(y):
                seconds += 86400
        for m in range(1, self.month):
            seconds += ObsTime.__day_per_month[m - 1] * 86400
            if (m == 2) and ObsTime.isLeapYear(self.year):
                seconds += 86400
        seconds += (self.day - 1) * 86400
        seconds += self.hour * 3600
        seconds += self.min * 60
        seconds += self.sec
        seconds += self.ms / 1000.0

        return seconds

    @staticmethod
    def random() -> ObsTime:   
        """Generate random date between 01/01/1970 and 01/01/2050"""
        t0 = ObsTime(2050, 1, 1, 0, 0, 0, 0)
        s0 = t0.toAbsTime()
        return ObsTime.readUnixTime(random.random() * s0)
    
    @staticmethod
    def now() -> ObsTime:   
        """Get Current Date and Time"""
        from datetime import datetime
        nowobj = datetime.now()
        
        tps = ObsTime(nowobj.year, nowobj.month, nowobj.day, 
                     nowobj.hour, nowobj.minute, nowobj.second, 0)
        return tps

    def printZone(self) -> str:   
        """Print zone code (Z if greenwhich) ISO 8601"""
        if self.zone == 0:
            return "Z"
        else:
            if self.zone > 0:
                return "+" + "{:02d}".format(self.zone) + ":00"
            else:
                return "-" + "{:02d}".format(abs(self.zone)) + ":00"

    def timeWithZone(self) -> str:   
        """Print as Gpx time"""
        fmt_save = ObsTime.getPrintFormat()
        ObsTime.setPrintFormat("4Y-2M-2DT2h:2m:2s")
        output = str(self) + self.printZone()
        ObsTime.setPrintFormat(fmt_save)
        return output

    def convertToZone(self, zone: int) -> ObsTime:   
        """Zone conversion

        :param zone: Time zone
        :return: Time for the set time zone
        """
        shift = zone - self.zone
        new_time = ObsTime.readUnixTime(self.toAbsTime() + 3600 * shift)
        new_time.zone = zone
        return new_time

    def getDayOfWeek(self) -> str:   
        """Return the current day of week"""
        seconds = self.toAbsTime()
        return ObsTime.__day_names[
            ((int)(seconds / 86400) + ObsTime.__day_of_base_date) % 7
        ]

    def __fillMember(self, value, code):
        """Adding value in a field according to code"""
        if code[1] == "D":
            self.day = (int)(value)
        if code[1] == "M":
            self.month = (int)(value)
        if code[1] == "h":
            self.hour = (int)(value)
        if code[1] == "m":
            self.min = (int)(value)
        if code[1] == "s":
            self.sec = (int)(value)
        if code == "2Y":
            self.year = (int)(value) + ObsTime.BASE_YEAR
        if code == "4Y":
            self.year = (int)(value)
        if code[1] == "z":
            self.ms = (int)(value) * 10 ** (3 - (int)(code[0]))

    @staticmethod
    def __takeSecond(elem):
        """Methods to prepare reading timestamp format"""
        return elem[1]

    @staticmethod
    def __rep(char: str, n: int) -> str:   
        """Generate a string repeting a char

        :param char: Caracter to repeate
        :param n: Number or repetitions
        :retunr: A string of `n` repetitions of `c`
        """
        output = ""
        for i in range(n):
            output += char
        return output

    @staticmethod
    def __precompileReadFmt(format: str) -> list[tuple[str, int]]:   
        """Precompile the reader

        :param format: A format string
        :return: A list of precompiled symbols
        """

        shift = 0
        PRECOMPILED_LIST = []

        # Replacing '*' symbols
        index = format.find("*")
        while index >= 0:
            n = (int)(format[index - 1])
            format = format[: index - 1] + ObsTime.__rep("x", n) + format[index + 1 :]
            index = format.find("*")

        # Filling preccompiled list
        for i in range(len(ObsTime.__codes)):
            code = ObsTime.__codes[i]
            index = format.find(code)
            if index < 0:
                continue
            PRECOMPILED_LIST.append((code, index))
        PRECOMPILED_LIST.sort(key=ObsTime.__takeSecond)

        # Shift to manage '4Y', '1X' and '3z' symbols
        for i in range(len(PRECOMPILED_LIST)):
            PRECOMPILED_LIST[i] = (
                PRECOMPILED_LIST[i][0],
                PRECOMPILED_LIST[i][1] + shift,
            )
            shift += (int)(PRECOMPILED_LIST[i][0][0]) - 2

        return PRECOMPILED_LIST

    @staticmethod
    def readTimestamp(timeAsString: str) -> ObsTime:   
        """Build timestamp from string according to READ_FMT

        :param timeAsString: Timestamp in string format
        """

        time = ObsTime()
        PCL = ObsTime.__PRECOMPILED_READ_FMT

        for i in range(len(PCL)):
            index = PCL[i][1]
            time.__fillMember(
                timeAsString[index : index + (int)(PCL[i][0][0])], PCL[i][0]
            )

        return time

    # ------------------------------------------------------------
    # Remplacing substring of length 'length', starting at pos id
    # in string 'chaine' with new string 'new'
    # ------------------------------------------------------------
    @staticmethod
    def __replace(chaine: str, id: int, length: int, new: str) -> str:   
        """Remplacing substring of length `length`, starting at pos `id`
        in string `chaine` with new string `new`

        :param chaine: String to remplace
        :param id: Starting position of replacement
        :param length: Length of substring to remplace
        :param new: String of replacement
        :return: Replaced string
        """
        return chaine[:id] + new + chaine[id + length :]

    def __str__(self) -> str:   
        """Prints timestamp according to PRINT_FMT specification

        :retunr: the timestamp to print
        """

        subst = [
            self.day,
            self.day,
            self.month,
            self.month,
            self.year % 100,
            self.year,
            self.hour,
            self.hour,
            self.min,
            self.min,
            self.sec,
            self.sec,
            (int)((self.ms + 50) / 100),
            (int)((self.ms + 5) / 10),
            self.ms,
        ]

        output = ObsTime.__PRINT_FMT

        for i in range(len(ObsTime.__codes)):
            code = ObsTime.__codes[i]
            index = output.find(code)
            while index >= 0:
                value = (int)(code[0])
                output = ObsTime.__replace(
                    output, index, 2, ObsTime.__fmt_nd[value - 1].format(subst[i])
                )
                index = output.find(code)
        index = output.find("\\")
        while index >= 0:
            output = ObsTime.__replace(output, index, 1, "")
            index = output.find("@")

        return output

    def addSec(self, nb: int) -> ObsTime:   
        """Add `nb` seconds to current time

        :param nb: Number of seconds to add
        :return: A :class:`ObsTime` incremented of `nb` second(s)
        """
        sec = self.toAbsTime() + nb
        return ObsTime.readUnixTime(sec)

    def addMin(self, nb: int) -> ObsTime:   
        """Add `nb` minutes to current time

        :param nb: Number of minutes to add
        :return: A :class:`ObsTime` incremented of `nb` minute(s)
        """
        sec = self.toAbsTime() + nb * 60
        return ObsTime.readUnixTime(sec)

    def addHour(self, nb):
        """Add `nb` hours to current time

        :param nb: Number of hours to add
        :return: A :class:`ObsTime` incremented of `nb` hour(s)
        """
        sec = self.toAbsTime() + nb * 3600
        return ObsTime.readUnixTime(sec)

    def addDay(self, nb):
        """Add `nb` days to current time

        :param nb: Number of days to add
        :return: A :class:`ObsTime` incremented of `nb` day(s)
        """
        sec = self.toAbsTime() + nb * 86400
        return ObsTime.readUnixTime(sec)

    def __sub__(self, time: ObsTime) -> float:   
        """Difference between 2 dates

        :param time: :class:`ObsTime` to substract
        :return: Difference (in floating point seconds) between 2 date
        """
        return self.toAbsTime() - time.toAbsTime()

    def __eq__(self, time: ObsTime) -> bool:   
        """Tests if two timestamps are strictly equal (up to 1 ms)

        :param time: :class:`ObsTime` to compare
        """
        if self.ms != time.ms:
            return False
        if self.sec != time.sec:
            return False
        if self.min != time.min:
            return False
        if self.hour != time.hour:
            return False
        if self.day != time.day:
            return False
        if self.month != time.month:
            return False
        if self.year != time.year:
            return False
        return True

    def __ne__(self, time: ObsTime) -> bool:   
        """Test if two timestamps are different

        :param time: :class:`ObsTime` to compare
        """
        return not (time == self)

    def __gt__(self, time: ObsTime) -> bool:   
        """Tests chronological order of two timestamps

        :param time: :class:`ObsTime` to compare
        """
        if self.year != time.year:
            return self.year > time.year
        if self.month != time.month:
            return self.month > time.month
        if self.day != time.day:
            return self.day > time.day
        if self.hour != time.hour:
            return self.hour > time.hour
        if self.min != time.min:
            return self.min > time.min
        if self.sec != time.sec:
            return self.sec > time.sec
        return self.ms > time.ms

    def __lt__(self, time: ObsTime) -> bool:   
        """Tests chronological order of two timestamps

        :param time: :class:`ObsTime` to compare
        """
        if self.year != time.year:
            return self.year < time.year
        if self.month != time.month:
            return self.month < time.month
        if self.day != time.day:
            return self.day < time.day
        if self.hour != time.hour:
            return self.hour < time.hour
        if self.min != time.min:
            return self.min < time.min
        if self.sec != time.sec:
            return self.sec < time.sec
        return self.ms < time.ms

    def __ge__(self, time: ObsTime) -> bool:   
        """Inverse of :method:`__gt__`

        :param time: :class:`ObsTime` to compare
        """

        return not (self < time)

    def __le__(self, time: ObsTime) -> bool:   
        """Inverse of :method:`__lt__`

        :param time: :class:`ObsTime` to compare
        """
        return not (self > time)
