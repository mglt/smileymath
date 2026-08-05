#!/usr/bin/python3
from time import time
import secrets
#from random import randint
from statistics import mean
from math import ceil
#from ascii_fig import AsciiFig
#import sys
#import sys.stdout
import smileymath.user_input
import smileymath.ascii_fig

class Challenge:
  def __init__( self, question:str, answer:str, 
                index:int=None, timeout:int=None ):
    """Challenge with response of type string expected 

    args:
      question : th equestion shown to the end user. Could be of any type.
      answer (str): the response expected from the end user. 
        The type needs to match the one provided by the end user, 
        that is edefined by the UserInput. 
      index (int) is an optional parameter that indicates the number 
        of question. By default, it is set to None
      timeout (int): indicate sthe time left to the end user to respond.
    """
    self.answer = answer
    if isinstance( index, int ) is True :
      self.question = f"{ index}: {question}"
    else:
      self.question = f"{question}"
    self.timeout = timeout

    self.user_resp = None
    self.time = None
    self.score = 0

  def get_user_resp( self ):
    """ collects the end user input """
    user_response = smileymath.user_input.UserInput( timeout=self.timeout )
    self.user_resp = user_response.get_user_input( )

  def evaluate_user_resp( self ):
    """ evaluates the user response

    compare the user response (self.user_resp) to the expected
    answer (self.answer)
    """
#    print( f"evaluate: self.user_resp: {self.user_resp} {type(self.user_resp)}" )
#    print( f"evaluate: self.answer: {self.answer} {type(self.answer)}" )
    if self.user_resp == self.answer:
      self.score = 1

  def ask( self ):
    print( self.question, end="", flush=True )
    time_start = time()
    self.get_user_resp( )
    self.time = time() - time_start
    self.evaluate_user_resp( )


class IntChallenge( Challenge ):
  """Challenge with response of type int expected"""

  def __init__( self, question:str, answer:str, 
                index:int=None, timeout:int=None ):
    super().__init__( question, answer, index=index, timeout=timeout)

  def get_user_resp( self ):
    user_response = smileymath.user_input.IntUserInput( timeout=self.timeout )
    self.user_resp = user_response.get_user_input( )

class DoubleIntChallenge( Challenge ):
  """Challenge with response of type int expected"""

  def __init__( self, question:str, answer:str, 
                index:int=None, timeout:int=None ):
    super().__init__( question, answer, index=index, timeout=timeout)

  def get_user_resp( self ):
    user_response = smileymath.user_input.DoubleIntUserInput( timeout=self.timeout )
    self.user_resp = user_response.get_user_input( )

class HourMinuteChallenge( Challenge ):
  """Challenge with response of type datetime expected

  While datetime provides a complete object, the input from 
  the user is expected to be limited to hours and minutes
  """

  def __init__( self, question:str, answer:str, 
                index:int=None, timeout:int=None ):
    super().__init__( question, answer, index=index, timeout=timeout)

  def get_user_resp( self ):
    user_response = smileymath.user_input.HourMinuteDateTimeUserInput( \
                      timeout=self.timeout )
    self.user_resp = user_response.get_user_input( )

  def evaluate_user_resp( self ):
    """ only hours and minutes are compared """
    if isinstance( self.user_resp, datetime.datetime ) and\
       isinstance( self.answer, datetime.datetime ):
      if ( self.user_resp.minute == self.answer.minute ) and \
         ( self.user_resp.hour == self.answer.hour ):
        self.score = 1



class AdditionSet:

  def __init__( self, challenge_nbr = 20, ascii_fig=None, timeout=None, **kwargs ):
    """ generates challenge_nbr questions for table y """
 
    self.kwargs = kwargs
    self.challenge_nbr = challenge_nbr
    self.timeout = timeout
    self.ascii_fig = smileymath.ascii_fig.get_db( ascii_fig )
    self.welcome( )
    ## building challenges
    self.score = 0
    self.time = 0
    self.missed_challenge_list = []
    for i in range( challenge_nbr ) :
      challenge = self.get_challenge( index=i+1 )
      challenge.ask( )
      self.score += challenge.score
      self.time += challenge.time
      if challenge.score == 0:
        self.missed_challenge_list.append( challenge )
    self.score = self.score / challenge_nbr * 100.0
    self.time /= challenge_nbr
    self.finalize()

  def name( self ):
    return "adding"

  def welcome( self ):
    txt = f"Hi! \nLet's practice {self.name()} "
    if 'y' in self.kwargs.keys():
      txt += f"{self.kwargs[ 'y' ][ 0 ]}-{self.kwargs[ 'y' ][ 1 ]} "
    txt += f"with {self.challenge_nbr} challenges\n"
    print( txt )

  def pick_rand( self, key ):
    """pick a random number within values indicated for the set """

    if key in self.kwargs.keys():
      if isinstance( self.kwargs[ key ], list ):
        if len( self.kwargs[ key ] ) == 2:
          inf = self.kwargs[ key ][ 0 ]
          sup = self.kwargs[ key ][ 1 ]
          return secrets.choice( [ inf + i for i in range( sup + 1 - inf ) ] )
    raise ValueError( f"unable to pick a random value for {key} "\
                       f"in {self.kwargs}" )

  def get_challenge(self, index=None):
    """ generates a question of type x + y """
    x = self.pick_rand( 'x' )
    y = self.pick_rand( 'y' )
    return IntChallenge( f"{x} + {y} = ", x + y, index=index, timeout=self.timeout ) 
      

  def finalize(self):

    if self.score == 100 :
      print( "SUPER !!!!! SUPER !!! SUPER !!!!" )
      print( "100% - 100% - 100% - 100% - 100%" )
    elif self.score > 50: 
      print("Congratulation!")

    if self.score != 100:
      print("Let's check some of the questions...")
      for challenge in self.missed_challenge_list:
        while challenge.score == 0:
          challenge.ask()
      print( f"Super! Your score was {ceil(self.score)}%% and is now 100%%!")

    print("Your mean response time is: %.2f"%self.time )
    if self.ascii_fig != None:
      print(self.ascii_fig.pick_fig( self.score ) )


class ComplementTo10Set( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )
  def name( self ):
    return "complementing to 10"

  def get_challenge(self, index=None ):
    """ generates a question of type x + ? = 10 """
    x = self.pick_rand( 'x' )
    return IntChallenge( f"{x} + ? = 10  ", 10 - x, index=index,\
                         timeout=self.timeout ) 


class SubtractionSet( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )
  def name( self ):
    return "subtracting"

  def get_challenge(self, index=None ):
    """ generates a question of type x - y """

    x = self.pick_rand( 'x' )
    y = self.pick_rand( 'y' )
    m = min( [ x, y ] )
    M = max( [ x, y ] )
    return IntChallenge( f"{M} - {m} = ", M - m, index=index,\
                         timeout=self.timeout ) 


class MultiplicationSet( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )
  def name( self ):
    return "multiplying"

  def get_challenge(self, index=None ):
    """ generates a question of type x x y """
    x = self.pick_rand( 'x' )
    y = self.pick_rand( 'y' )
    return IntChallenge( f"{x} x {y} = ", x*y, index=index,\
                         timeout=self.timeout ) 


class DivisionSet( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )
  def name( self ):
    return "dividing"

  def get_challenge(self, index=None ):
    """ generates a question of type x / y """
    x = self.pick_rand( 'x' )
    y = self.pick_rand( 'y' )
    m = x * y
    return IntChallenge( f"{m} / {x} = ", y, index=index,\
                         timeout=self.timeout ) 

class DivisionWithRemainderSet( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )
  def name( self ):
    return "dividing"

  def get_challenge(self, index=None ):
    """ generates a question of type x / y """
    
    x = self.pick_rand( 'x' )
    y = self.pick_rand( 'y' )
    while x == 0 or y == 0 :
      x = self.pick_rand( 'x' )
      y = self.pick_rand( 'y' )
    m = min( [ x, y ] )
    M = max( [ x, y ] )
    d = int( M / m )
    r = M - d * m
#    print( f"m: {m}, M: {M}, d:{d}, r:{r}" )
#    print( f"get_challenge: {( d, r )} {type(d)}/{type(r)}" ) 
    return DoubleIntChallenge( f"{M} / {m} = ", ( d, r ),\
           index=index, timeout=self.timeout  ) 

  def welcome( self ):
    super().welcome( )
    print( "Example of response's format: 13 / 6 = 2 1\n" )

import datetime

class HourMinuteAdditionSet( AdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :

    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )

  def txt( self, date_time_obj ) ->str :
    """ outputs hours:min from date_time_obj"""
    if isinstance( date_time_obj, datetime.datetime ) :
      string = f"{date_time_obj.hour}:{date_time_obj.minute}"
    elif isinstance( date_time_obj, datetime.timedelta ) :
      string = f"{date_time_obj.hours}:{date_time_obj.minutes}"
    else:
      raise ValueError( f"unexpected type {type(date_time_obj)}" )
    return string

  def name( self ):
    return "adding time"

  def welcome( self ):
    super().welcome( )
    print( "Example of response's format: 11:10 + 3:20 = 14:30\n" )


  def get_challenge(self, index=None ):
    """ generates a question of type datetime """
    ## should be in __init__
    self.kwargs[ 'minutes' ] =  [ 0, 59 ]
    self.kwargs[ 'hours' ] = [ 0, 23 ]

    start = datetime.datetime( year=1911, month=5, day=18,\
                        hour=self.pick_rand( 'hours' ), \
                        minute=self.pick_rand( 'minutes' ) )
    delta_hours = self.pick_rand( 'hours' )
    delta_minutes = self.pick_rand( 'minutes' )
    delta = datetime.timedelta( hours=delta_hours, \
                                     minutes=delta_minutes )
    answer = start + delta
    question = f"{start.hour}:{start.minute} + {delta_hours}:{delta_minutes} = "
    return HourMinuteChallenge( question, answer, \
             index=index, timeout=self.timeout )

class HourMinuteSubstractionSet( HourMinuteAdditionSet ):

  def __init__( self, challenge_nbr = 20, ascii_fig=None, \
                timeout=None, **kwargs ) :
    super().__init__( challenge_nbr=challenge_nbr, \
                      ascii_fig=ascii_fig, timeout=timeout, \
                      **kwargs )

  def name( self ):
    return "subtracting time"

  def welcome( self ):
    super().welcome( )
    print( "Example of response's format: 14:30 - 3:20 = 11:10\n" )

  def get_challenge(self, index=None ):
    """ generates a question of type datetime """

    ## should be in __init__
    self.kwargs[ 'minutes' ] =  [ 0, 59 ]
    self.kwargs[ 'hours' ] = [ 0, 23 ]

    start = datetime.datetime( year=1911, month=5, day=18,\
                        hour=self.pick_rand( 'hours' ), \
                        minute=self.pick_rand( 'minutes' ) )
    delta_hours = self.pick_rand( 'hours' )
    delta_minutes = self.pick_rand( 'minutes' )
    delta = datetime.timedelta( hours=delta_hours, \
                                     minutes=delta_minutes ) 
    answer = start - delta
    question = f"{start.hour}:{start.minute} - {delta_hours}:{delta_minutes} = "
    return HourMinuteChallenge( question, answer, \
             index=index, timeout=self.timeout )


