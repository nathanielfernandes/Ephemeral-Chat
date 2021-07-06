import time


class Ratelimit:
    __slots__ = ("rate", "per", "_timeFrame", "_remainingCalls", "_lastCall")

    def __init__(self, rate: int, per: float):
        self.rate = int(rate)
        self.per = float(per)

        self._timeFrame = 0.0  # time of the first call within the time frame
        self._remainingCalls = (
            self.rate
        )  # the remaining calls left before being on cooldown
        self._lastCall = 0.0  # time of the last call made

    def _isStale(self, ct=None):
        ct = ct or time.time()
        return ct > self._timeFrame + self.per

    def get_remainingCalls(self, ct=None) -> int:
        ct = ct or time.time()
        remaining = self._remainingCalls

        # if the current time is > than timeFrame + per then reset remaining
        if self._isStale(ct):
            remaining = self.rate

        return remaining

    def update_calls(self) -> bool:
        # set last call to the current time
        self._lastCall = ct = time.time()

        self._remainingCalls = self.get_remainingCalls(ct)

        # if all remaning calls are available then start a new time frame
        if self._remainingCalls == self.rate:
            self._timeFrame = ct

        # is on cooldown
        if self._remainingCalls == 0:
            return False

        self._remainingCalls -= 1
        return True


class RatelimitManager:
    def __init__(self, rate: int, per: float):
        self.rate = int(rate)
        self.per = float(per)
        self._ratelimitMapping = {}

    def _cleanseMapping(self):
        # deletes any stale cooldowns
        ct = time.time()

        stale = [k for k, v in self._ratelimitMapping.items() if v._isStale(ct)]
        for k in stale:
            del self._ratelimitMapping[k]

    def check_ratelimit(self, identifier) -> bool:
        self._cleanseMapping()
        if identifier in self._ratelimitMapping:
            return self._ratelimitMapping[identifier].update_calls()

        newCD = Ratelimit(self.rate, self.per)
        self._ratelimitMapping[identifier] = newCD

        return newCD.update_calls()
