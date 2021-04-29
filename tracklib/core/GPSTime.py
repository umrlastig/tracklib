# ------------------------ GPSTime -------------------------------
# Class to manage timestamps
# ----------------------------------------------------------------
import copy
import random

class GPSTime:

    BASE_YEAR = 2000

    __READ_FMT = "2D/2M/4Y 2h:2m:2s"
    __PRINT_FMT = "2D/2M/4Y 2h:2m:2s"
    __PRECOMPILED_READ_FMT = [('2D', 0), 
                              ('2M', 3), 
                              ('4Y', 6), 
                              ('2h', 11), 
                              ('2m', 14), 
                              ('2s', 17)]
    
    __fmt_nd = ['{:01d}', '{:02d}', '{:03d}', '{:04d}']
    __codes  = ["1D", "2D", "1M", "2M", "2Y", "4Y", 
            "1h", "2h", "1m", "2m", "1s", "2s", "1z", "2z", "3z"]
            
    __day_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    __month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    __day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    __day_of_base_date = 3    # Thu 01/01/1970

    
    # ------------------------------------------------------------    
    # Default value : 01/01/1970 00:00:00.000
    # ------------------------------------------------------------    
    def __init__(self, year=1970, month=1, day=1, hour=0, min=0, sec=0, ms=0):
    
        if isinstance(year, str):
        
            time = GPSTime.readTimestamp(year)
            self.day   = time.day
            self.month = time.month
            self.year  = time.year
            self.hour  = time.hour
            self.min   = time.min
            self.sec   = time.sec
            self.ms    = time.ms
            
        else:
        
            self.day   = day
            self.month = month
            self.year  = year
            self.hour  = hour
            self.min   = min
            self.sec   = sec
            self.ms    = ms
            
    def copy(self):
        return copy.deepcopy(self)
        
    @staticmethod
    def setPrintFormat(format):
        GPSTime.__PRINT_FMT = format    
        
    @staticmethod
    def setReadFormat(format):
        GPSTime.__READ_FMT = format
        GPSTime.__PRECOMPILED_READ_FMT = GPSTime.__precompileReadFmt(GPSTime.__READ_FMT)
        
    @staticmethod
    def getPrintFormat():
        return GPSTime.__PRINT_FMT
    
    @staticmethod
    def getReadFormat():
        return GPSTime.__READ_FMT
        
    # ------------------------------------------------------------
    # Converting elapsed float seconds since 01/01/1970 in GPSTime
    # Warning: does not consider leap seconds (31 since 1970)
    # ------------------------------------------------------------    
    @staticmethod
    def readUnixTime(elapsed_seconds):
    
        time = GPSTime()
        
        SECOND_PER_YEAR = 86400*365
        SECOND_PER_MONTH = 86400*28
        
        # Year
        sec = 0
        year = 1970
        while (sec < elapsed_seconds - SECOND_PER_YEAR):
            sec += SECOND_PER_YEAR
            if (year % 4 == 0):
                sec += 86400
            year += 1
        time.year = year
        elapsed_seconds -= sec

        # Month
        month = 0
        for i in range(12):
            sec_on_month = GPSTime.__day_per_month[month]*86400
            if ((month == 1) and (year % 4 == 0)):
                sec_on_month += 86400
            if (elapsed_seconds < sec_on_month):
                break
            elapsed_seconds -= sec_on_month
            month += 1
            
        
        time.month = month+1
        
        # Day
        time.day = (int)(elapsed_seconds/86400)+1
        elapsed_seconds -= (time.day-1)*86400
        
        # Hour
        time.hour = (int)(elapsed_seconds/3600)
        elapsed_seconds -= time.hour*3600
        
        # Minute
        time.min = (int)(elapsed_seconds/60)
        elapsed_seconds -= time.min*60
        
        # Second
        time.sec = (int)(elapsed_seconds)
        elapsed_seconds -= time.sec
        
        # Milisecond
        time.ms = (int)(elapsed_seconds*1000)
        
        return time
        
    # ------------------------------------------------------------
    # Converting to elapsed float seconds since 01/01/1970
    # Warning: does not consider leap seconds (31 since 1970)
    # ------------------------------------------------------------    
    def toAbsTime(self):
        seconds = 0
        for y in range(1970, self.year):
            seconds += 86400*365
            if (y % 4 == 0):
                seconds += 86400
        for m in range(1, self.month):
            seconds += GPSTime.__day_per_month[m-1]*86400
            if ((m == 2) and (self.year % 4 == 0)):
                seconds += 86400
        seconds += (self.day-1)*86400
        seconds += self.hour*3600
        seconds += self.min*60
        seconds += self.sec
        seconds += self.ms/1000.0
        
        return seconds
    
    # ------------------------------------------------------------
    # Generate random date between 01/01/1970 and 01/01/2050
    # ------------------------------------------------------------    
    def random():
        t0 = GPSTime(2050,1,1,0,0,0,0)
        s0 = t0.toAbsTime()
        return GPSTime.readUnixTime(random.random()*s0)
        
    # ------------------------------------------------------------
    # Computing current day of week
    # ------------------------------------------------------------    
    def getDayOfWeek(self):
        seconds = self.toAbsTime()
        return GPSTime.__day_names[((int)(seconds/86400) + GPSTime.__day_of_base_date) % 7]
        

    # ------------------------------------------------------------
    # Adding value in a field according to code 
    # ------------------------------------------------------------    
    def __fillMember(self, value, code):
        if (code[1] == "D"):
            self.day = (int)(value)
        if (code[1] == "M"):
            self.month = (int)(value)
        if (code[1] == "h"):
            self.hour = (int)(value)
        if (code[1] == "m"):
            self.min = (int)(value)
        if (code[1] == "s"):
            self.sec = (int)(value)
        if (code == "2Y"):
            self.year = (int)(value) + GPSTime.BASE_YEAR
        if (code == "4Y"):
            self.year = (int)(value)
        if (code[1] == "z"):
            self.ms = (int)(value)*10**(3-(int)(code[0]))
        
    # ------------------------------------------------------------    
    # Methods to prepare reading timestamp format
    # ------------------------------------------------------------        
    @staticmethod
    def __takeSecond(elem):
        return elem[1]
        
    @staticmethod
    def __rep(char, n):
        output = ""
        for i in range(n):
            output += char
        return output
        
    @staticmethod
    def __precompileReadFmt(format):
    
        shift = 0
        PRECOMPILED_LIST = []
    
        # Replacing '*' symbols
        index = format.find("*")
        while(index >= 0):
            n = (int)(format[index-1])
            format = format[:index-1] + GPSTime.__rep('x', n) + format[index+1:]
            index = format.find("*")
        
        # Filling preccompiled list
        for i in range(len(GPSTime.__codes)):
            code = GPSTime.__codes[i]
            index = format.find(code)
            if (index < 0):
                continue
            PRECOMPILED_LIST.append((code, index))
        PRECOMPILED_LIST.sort(key=GPSTime.__takeSecond)
        
        # Shift to manage '4Y', '1X' and '3z' symbols
        for i in range(len(PRECOMPILED_LIST)):
            PRECOMPILED_LIST[i] = (PRECOMPILED_LIST[i][0], PRECOMPILED_LIST[i][1] + shift)
            shift += (int)(PRECOMPILED_LIST[i][0][0])-2 
        
        return PRECOMPILED_LIST

    # ------------------------------------------------------------    
    # Build timestamp from string according to READ_FMT
    # ------------------------------------------------------------        
    @staticmethod
    def readTimestamp(timeAsString):

        time = GPSTime()
        PCL = GPSTime.__PRECOMPILED_READ_FMT
        
        for i in range(len(PCL)):
            index = PCL[i][1]
            time.__fillMember(timeAsString[index:index+(int)(PCL[i][0][0])], PCL[i][0])
            
        return time
                
    # ------------------------------------------------------------
    # Remplacing substring of length 'length', starting at pos id
    # in string 'chaine' with new string 'new' 
    # ------------------------------------------------------------    
    @staticmethod
    def __replace(chaine, id, length, new):
        return chaine[:id] + new + chaine[id + length:]
        
        
    # ------------------------------------------------------------
    # Prints timestamp according to PRINT_FMT specification
    # ------------------------------------------------------------
    def __str__(self):
        
        subst = [self.day, self.day, self.month, self.month, self.year % 100, self.year,
            self.hour, self.hour, self.min, self.min, self.sec, self.sec, 
            (int)((self.ms+50)/100), (int)((self.ms+5)/10), self.ms]

        output = GPSTime.__PRINT_FMT
        
        for i in range(len(GPSTime.__codes)):
            code = GPSTime.__codes[i]
            index = output.find(code)
            while (index >= 0):
                value = (int)(code[0])
                output = GPSTime.__replace(output, index, 2, GPSTime.__fmt_nd[value-1].format(subst[i]))
                index = output.find(code)
        index = output.find("\\")
        while (index >= 0):
            output = GPSTime.__replace(output, index, 1, "")
            index = output.find("@")
            
        return output
    
    # ------------------------------------------------------------
    # Increment or decrement date
    # ------------------------------------------------------------
    def addSec(self, nb):
        sec = self.toAbsTime() + nb
        return GPSTime.readUnixTime(sec)
    def addMin(self, nb):
        sec = self.toAbsTime() + nb*60
        return GPSTime.readUnixTime(sec)
    def addHour(self, nb):
        sec = self.toAbsTime() + nb*3600
        return GPSTime.readUnixTime(sec)
    def addDay(self, nb):
        sec = self.toAbsTime() + nb*86400
        return GPSTime.readUnixTime(sec)
        
    # ------------------------------------------------------------
    # Difference (in floating point seconds) between 2 dates
    # ------------------------------------------------------------
    def __sub__(self, time):
        return self.toAbsTime() - time.toAbsTime()
    
    # ------------------------------------------------------------
    # Tests if two timestamps are strictly equal (up to 1 ms)
    # ------------------------------------------------------------
    def __eq__(self, time):
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

    def __ne__(self, time):
        return not (time == self)
   
       
    # ------------------------------------------------------------
    # Tests chronological order of two timestamps
    # ------------------------------------------------------------   
    def __gt__(self, time):
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
           
    def __lt__(self, time):
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
       
    def __ge__(self, time):
        return not (self < time)
    def __le__(self, time):
        return not (self > time)
    
    
        
        
        
        