from pynput import keyboard
import signal
import sys
import termios
import tty
import time
import datetime
import logging

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

  def __init__( self, txt="", timeout=None, end_of_input=keyboard.Key.enter ) :
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

#  def debug( self, function, message ):
#    """tools used for debugging """
#    if self.debug_state is True:
#      self.log.debug( f"DEBUG: {function} : {message}")

  def get_user_input( self ):
    """ starts a keyboard listener and get user input """
    input_value = None
    self.input_key_list = []

    # Suppress terminal echo so typed keys don't leak to the shell
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(fd)
      # Restore only echo/canonical mode but keep raw for pynput
      new_settings = termios.tcgetattr(fd)
      # Disable echo (ECHO) and canonical mode (ICANON) 
      # but keep output processing (OPOST) for proper newlines
      new_settings[3] = new_settings[3] & ~termios.ECHO & ~termios.ICANON
      new_settings[1] = new_settings[1] | termios.OPOST
      termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

      listener = keyboard.Listener( on_press=self.on_press, 
                                    on_release=self.on_release)
      if self.timeout is None :
        listener.start()
        listener.wait()  # ensure the listener is ready before accepting keys
        listener.join( )
      else:
        try:
          with Timeout( self.timeout ):
            listener.start()
            listener.wait()  # ensure the listener is ready
            listener.join( )
        except Timeout.Timeout :
          if keyboard.Key.enter not in self.input_key_list :
            print("")
      
      listener.stop()
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

  def get_input_string( self ):
    """reads the input provided """
  
    self.log.debug( f"input_key_list: {self.input_key_list}" )
    string = ""
    for k in self.input_key_list:
      if k == keyboard.Key.space:
        string += ' '
      elif k == keyboard.Key.enter:
        pass  # end of input marker, not part of the string
      elif hasattr(k, 'char') and k.char is not None:
        string += k.char
    self.log.debug( f"input_string (from input_key_list): {string.strip()}" )
    return string.strip()
  
  def format_input( self, input_string:str ):
    """converts the resulting string intyo the appropriated format 

    In this example, the full string is returned without any format
    operation. 
    """
#    print(f"check_format str: {input_string}" )
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
#      self.debug( "check_format", f"Error {type(e)} while formating {input_string}" ) 
      self.log.debug( f"Error {type(e)} while formating {input_string}" ) 
      return False
  
  
  def on_press(self, key):
    """ action performed uppon pressin a key

    It is worth noting that action can also be performed on release 
    of the key.
    We only act uppon pressin the key. 
    It is worth noting that when a char results from the combination 
    of multiple keys 'like shift + char' key.char is properly displayed.  
    """
#    ## special key to enable debugging
#    ## during a session
#    if key == keyboard.Key.esc:
#      self.debug_state = not self.debug_state 
    ## we do print the pressed character as we noticed that with USB keyboard
    ## some specific key are not caught by the user_input (while being printed)
    ## In our case the number '5' is not considered by the num pad and is hardly 
    ## consider on the main part of the keyboard. 
    self.log.debug( f"pressed_key: {key}" )
    ## key representing a char — only store if it actually has content
    if hasattr( key, 'char') and key.char is not None:
      self.input_key_list.append( key )
    ## non character keys
    else: 
      ## backspace removes the last key 
      if key == keyboard.Key.backspace:
        if len( self.input_key_list ) > 0:
          self.input_key_list.pop( -1 )
      ## space is a valid input character
      elif key == keyboard.Key.space:
        self.input_key_list.append( key )
      ## end_of_input stops the listener, but only if the input format 
      ## is appropriate 
      elif key == self.end_of_input :
        if self.check_format( self.get_input_string( ) ) is True:
          self.input_key_list.append( key )
          # Stop listener
          return False 
        else:
          ## One problem is that when enter has been typed
          ## the cursor goes to the next line, and there is no 
          ## way for the end user to backspace.
          ## to make possible the end user to re-enter a response
          ## we re-initialize the self.input_key_list.
          ## 
          if self.end_of_input == keyboard.Key.enter:
            self.input_key_list = []
      ## ignore other special keys (shift, ctrl, alt, etc.)
      ## they don't contribute to the input string
  
  def on_release(self, key):
    """ actions performed on key released.
  
    We currenlty do not implement any specific action
    When the function returns False, the listener is stoped.
    """
    self.log.debug( f"released_key: {key}" )
    

class IntUserInput ( UserInput ):

  def __init__( self, txt="", timeout=None, end_of_input=keyboard.Key.enter ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
    return int( input_string.strip() )
#    self.log.debug( f"formatted_input: {formatted_input}" )
#    return formatted_input

class DoubleIntUserInput( UserInput ):
  """ inputs consists of two int separated by a space 

  Such input is expected for a division with remainder for example.
  Upon viewing "5 / 2 = ", th eend user is expected to type "2 1".
  This classe returns the int tuple (2, 1). 
  """

  def __init__( self, txt="", timeout=None, end_of_input=keyboard.Key.enter ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
#    input_string = input_string.strip( ) 
    split_input_string = input_string.split( ' ' )
    for i in range( len( split_input_string ) ):
      if split_input_string[ i ] == '':
        del split_input_string[ i ] 
    if len( split_input_string )  == 1:
      split_input_string.append( '0' )
    elif len( split_input_string )  != 2:
      raise ValueError( f"unexpected len for input_string" )
    return tuple( [ int( i.strip() ) for i in split_input_string ] )
#    self.log.debug( f"formatted_input: {formatted_input}" )
#    return formatted_input

class HourMinuteDateTimeUserInput( UserInput ):

  def __init__( self, txt="", timeout=None, end_of_input=keyboard.Key.enter ) :
    super().__init__( txt=txt, timeout=timeout, end_of_input=end_of_input )

  def format_input( self, input_string ):
    ## eventually only the hours are provided and minutes are omitted
    ## In this case we normalize 18 to 18:00
    if ':' not in input_string:
      input_string + ':00'
    time_format = "%H:%M"
    return datetime.datetime.strptime( input_string, time_format )

if __name__ == '__main__':
  ## In this example, we use 'esc' as the end of input 
  user_input = UserInput( timeout=10, end_of_input=keyboard.Key.esc )
  print( "Enter string response:" )
  value = user_input.get_user_input( )
  print( f"FIRST INPUT_VALUE: {value}" )
  print( "Enter a second string response:" )
  value = user_input.get_user_input( )
  print( f"SECOND INPUT_VALUE: {value}" ) 
