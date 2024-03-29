"""
Session storage class for Quixote 2.x.
"""

from time import time
from quixote import get_request

class Session:
    """
    Holds information about the current session.  The only information
    that is likely to be useful to applications is the 'user' attribute,
    which applications can use as they please.

    Instance attributes:
     * id : string
        the session ID (generated by SessionManager and used as the
        value of the session cookie)
     * user : any
        an object to identify the human being on the other end of the
        line.  It's up to you whether to store just a string in 'user',
        or some more complex data structure or object.
     * _remote_address : string
        IP address of user owning this session (only set when the
        session is created)
     * _creation_time : float
     * _access_time : float
        two ways of keeping track of the "age" of the session.
        Note that '__access_time' is maintained by the SessionManager that
        owns this session, using _set_access_time().

    Feel free to access 'id' and 'user' directly, but do not modify
    'id'.  The preferred way to set 'user' is with the set_user() method
    (which you might want to override for type-checking).

    Note: this class may be split into a SimpleSession superclass and a Session
    subclass in the future.
    """

    def __init__(self, id):
        """
        __init__ -- called only by `SessionManager.SessionManager`.
        """
        self.id = id
        self.user = None
        self._remote_address = get_request().get_environ("REMOTE_ADDR")
        #self._creation_time = self._access_time = time()
	self._creation_time = self._access_time = 0.0

    def __repr__(self):
        return "<%s at %x: %s>" % (self.__class__.__name__, id(self), self.id)

    def __str__(self):
        if self.user:
            return "session %s (user %s)" % (self.id, self.user)
        else:
            return "session %s (no user)" % self.id

    def has_info(self):
        """() -> boolean

        Return true if this session contains any information that must
        be saved.
        """
        return self.user

    def dump(self, file=None, header=True, deep=True):
        time_fmt = "%Y-%m-%d %H:%M:%S"
        ctime = strftime(time_fmt, localtime(self._creation_time))
        atime = strftime(time_fmt, localtime(self._access_time))

        if header:
            file.write('session %s:' % self.id)
        file.write('  user %s' % self.user)
        file.write('  _remote_address: %s' % self._remote_address)
        file.write('  created %s, last accessed %s' % (ctime, atime))

    def start_request(self):
        """
        Called near the beginning of each request: after the HTTPRequest
        object has been built, but before we traverse the URL or call the
        callable object found by URL traversal.
        """
        pass

    # -- Simple accessors and modifiers --------------------------------

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

    def get_remote_address(self):
        """Return the IP address (dotted-quad string) that made the
        initial request in this session.
        """
        return self._remote_address

    def get_creation_time(self):
        """Return the time that this session was created (seconds
        since epoch).
        """
        return self._creation_time

    def get_access_time(self):
        """Return the time that this session was last accessed (seconds
        since epoch).
        """
        return self._access_time

    def get_creation_age(self, _now=None):
        """Return the number of seconds since session was created."""
        # _now arg is not strictly necessary, but there for consistency
        # with get_access_age()
        return (_now or time()) - self._creation_time

    def get_access_age(self, _now=None):
        """Return the number of seconds since session was last accessed."""
        # _now arg is for SessionManager's use
        return (_now or time()) - self._access_time


    # -- Methods for SessionManager only -------------------------------

    def _set_access_time(self, resolution):
        now = time()
        if now - self._access_time > resolution:
            self._access_time = now
