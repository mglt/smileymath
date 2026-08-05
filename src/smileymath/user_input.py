import os
import signal
import sys
import termios
import tty
import time
import datetime
import logging


# Key constants (byte values in raw terminal mode)
class Key:
  """Constants for special keys in raw terminal mode."""
  ENTER = 'enter'
  SPACE = 'space'
  BACKSPACE = 'backspace'
  ESC = 'esc'


# Byte mappings for raw terminal input
_KEY_BYTES = {
    b'\r': Key.ENTER,
    b'\n': Key.ENTER,
    b' ': Key.SPACE,
    b'\x7f': Key.BACKSPACE,  # typical backspace
    b'\x08': Key.BACKSPACE,  # alternate backspace
    b'\x1b': Key.ESC,
}


class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()


class UserInput:

  def __init__( self, txt="", timeout=None, end_of_input=Key.ENTER ) :
    """ collects input user similarly to input
    
    In the geneal case, the response is typed, and by pressing "enter"
    the user sort of acknowledges this is the expected response.

    This class enriches the input functions as follows:
      1 It enables to specify with timeout for how long the user 
        can provide a repsonse. 
      2 The considered input from the end user is the one
        __effectively__ typed by the end user when either it presses 
        'enter' or when the timeout occurs. 
        This is a change compared to otherways where the end user 
        needs to press 'enter' before the timeout. In other words, 
        what he has typed is not considered unless 'enter' has been
        pressed. 
      3 The user cannot terminate the input monitoring until it has 
        provided an input that matches the expected format. 
        In particular this ovoids the case where the user types 
        'enter' and goes to the next question - voluntary or not.

    args:
      - timeout (int) : time in second while the user can type its response
      - end_of_user_input : character that indicates the end of the input. 
        By default the end of input is 'enter'.
    """
    self.input_key_list = []
    self.timeout = timeout
    self.end_of_input = end_of_input
    self.log = self.init_log( )

  def init_log( self ):
    log_file = './mymath.log'
    logger = logging.getLogger( __name__ )
    FORMAT = "[%(asctime)s : %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logger.setLevel( logging.DEBUG )
    logging.basicConfig(filename=log_file, format=FORMAT )
    return logger

  def get_user_input( self ):
    """ reads raw terminal input and returns the formatted value """
    input_value = None
    self.input_key_list = []

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      # Put terminal in raw mode to read individual keystrokes
      tty.setraw(fd)

      if self.timeout is None:
        self._read_keys(fd)
      else:
        try:
          with Timeout( self.timeout ):
            self._read_keys(fd)
        except Timeout.Timeout:
          if Key.ENTER not in self.input_key_list:
            print("")
    finally:
      # Restore original terminal settings
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
      # Flush any remaining input in the terminal buffer
      termios.tcflush(fd, termios.TCIFLUSH)

    try: 
      input_value = self.format_input( self.get_input_string( ) )
      self.log.debug( f"formatted input_value ({type( input_value )}) : {input_value}" )
    except Exception as e:
      self.log.debug( f"Error while formating {type(e)}:{e}" )
      
    return input_value

  def _read_keys(self, fd):
    """Read keystrokes one at a time until end_of_input or stopped."""
    while True:
      # Read one byte from stdin
      byte = os.read(fd, 1)
      if not byte:
        continue

      # Map byte to a key constant or a character
      key = _KEY_BYTES.get(byte)
      if key is None:
        # Regular character
        try:
          char = byte.decode('utf-8')
        except UnicodeDecodeError:
          continue
        # Ignore control characters (Ctrl+anything = 0x01-0x1a)
        if ord(char) < 32:
          continue
        self.input_key_list.append(char)
        self.log.debug(f"pressed_key: {char}")
      else:
        self.log.debug(f"pressed_key: {key}")
        if not self._handle_special_key(key):
          break

  def _handle_special_key(self, key):
    """Handle a special key. Returns False to stop reading, True to continue."""
    if key == Key.BACKSPACE:
      if len(self.input_key_list) > 0:
        self.input_key_list.pop(-1)
      return True
    elif key == Key.SPACE:
      self.input_key_list.append(Key.SPACE)
      return True
    elif key == self.end_of_input:
      if self.check_format(self.get_input_string()):
        self.input_key_list.append(key)
        return False  # Stop reading
      else:
        # Invalid format — reset input so user can re-enter
        if self.end_of_input == Key.ENTER:
          self.input_key_list = []
        return True
    else:
      # Ignore other special keys
      return True

  def get_input_string( self ):
    """reads the input provided """
  
    self.log.debug( f"input_key_list: {self.input_key_list}" )
    string = ""
    for k in self.input_key_list:
      if k == Key.SPACE:
        string += ' '
      elif k == Key.ENTER:
        pass  # end of input marker, not part of the string
      elif isinstance(k, str) and k not in (Key.ENTER, Key.SPACE, Key.BACKSPACE, Key.ESC):
        string += k
    self.log.debug( f"input_string (from input_key_list): {string.strip()}" )
    return string.strip()
  
  def format_input( self, input_string:str ):
    """converts the resulting string into the appropriated format 

    In this example, the full string is returned without any format
    operation. 
    """
    return input_string
  
  def check_format( self, input_string:str )-> bool:
    """checks the input string has the appropriated format
  
    Checking the format prevents the user to go to the next question 
    unless a valid response is provided. 
    In particular this, this prevents pressing 'enter' to the previous 
    question is considered by the current question. 
    This can occurs at least in two situations. 
    The first situation is when teh key is pressed for too long.
    The second is when the timeout occurs, before the user presses 'enter'
    """
    try:
      self.format_input( input_string ) 
      return True
    except Exception as e :
      self.log.debug( f"Error {type(e)} while formating {input_string}" ) 
      return False


class IntUserInput ( UserInput ):

  def __init__( self, txt="", timeout=None, end_of_input=Key.ENTER ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
    return int( input_string.strip() )


class DoubleIntUserInput( UserInput ):
  """ inputs consists of two int separated by a space 

  Such input is expected for a division with remainder for example.
  Upon viewing "5 / 2 = ", th eend user is expected to type "2 1".
  This classe returns the int tuple (2, 1). 
  """

  def __init__( self, txt="", timeout=None, end_of_input=Key.ENTER ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
    split_input_string = input_string.split( ' ' )
    for i in range( len( split_input_string ) ):
      if split_input_string[ i ] == '':
        del split_input_string[ i ] 
    if len( split_input_string )  == 1:
      split_input_string.append( '0' )
    elif len( split_input_string )  != 2:
      raise ValueError( f"unexpected len for input_string" )
    return tuple( [ int( i.strip() ) for i in split_input_string ] )


class HourMinuteDateTimeUserInput( UserInput ):

  def __init__( self, txt="", timeout=None, end_of_input=Key.ENTER ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
    ## eventually only the hours are provided and minutes are omitted
    ## In this case we normalize 18 to 18:00
    if ':' not in input_string:
      input_string += ':00'
    time_format = "%H:%M"
    return datetime.datetime.strptime( input_string, time_format )


if __name__ == '__main__':
  import os
  ## In this example, we use 'esc' as the end of input 
  user_input = UserInput( timeout=10, end_of_input=Key.ESC )
  print( "Enter string response:" )
  value = user_input.get_user_input( )
  print( f"FIRST INPUT_VALUE: {value}" )
  print( "Enter a second string response:" )
  value = user_input.get_user_input( )
  print( f"SECOND INPUT_VALUE: {value}" )
