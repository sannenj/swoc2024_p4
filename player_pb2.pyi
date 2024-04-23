from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    gameStateChange: _ClassVar[MessageType]
    playerJoined: _ClassVar[MessageType]
gameStateChange: MessageType
playerJoined: MessageType

class GameSettings(_message.Message):
    __slots__ = ("dimensions", "startAddress", "playerIdentifier", "gameStarted")
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    STARTADDRESS_FIELD_NUMBER: _ClassVar[int]
    PLAYERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    GAMESTARTED_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedScalarFieldContainer[int]
    startAddress: _containers.RepeatedScalarFieldContainer[int]
    playerIdentifier: str
    gameStarted: bool
    def __init__(self, dimensions: _Optional[_Iterable[int]] = ..., startAddress: _Optional[_Iterable[int]] = ..., playerIdentifier: _Optional[str] = ..., gameStarted: bool = ...) -> None: ...

class Move(_message.Message):
    __slots__ = ("playerIdentifier", "snakeName", "nextLocation")
    PLAYERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    SNAKENAME_FIELD_NUMBER: _ClassVar[int]
    NEXTLOCATION_FIELD_NUMBER: _ClassVar[int]
    playerIdentifier: str
    snakeName: str
    nextLocation: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, playerIdentifier: _Optional[str] = ..., snakeName: _Optional[str] = ..., nextLocation: _Optional[_Iterable[int]] = ...) -> None: ...

class SplitRequest(_message.Message):
    __slots__ = ("playerIdentifier", "oldSnakeName", "newSnakeName", "snakeSegment", "nextLocation")
    PLAYERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    OLDSNAKENAME_FIELD_NUMBER: _ClassVar[int]
    NEWSNAKENAME_FIELD_NUMBER: _ClassVar[int]
    SNAKESEGMENT_FIELD_NUMBER: _ClassVar[int]
    NEXTLOCATION_FIELD_NUMBER: _ClassVar[int]
    playerIdentifier: str
    oldSnakeName: str
    newSnakeName: str
    snakeSegment: int
    nextLocation: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, playerIdentifier: _Optional[str] = ..., oldSnakeName: _Optional[str] = ..., newSnakeName: _Optional[str] = ..., snakeSegment: _Optional[int] = ..., nextLocation: _Optional[_Iterable[int]] = ...) -> None: ...

class GameUpdateMessage(_message.Message):
    __slots__ = ("updatedCells", "removedSnakes", "playerScores")
    UPDATEDCELLS_FIELD_NUMBER: _ClassVar[int]
    REMOVEDSNAKES_FIELD_NUMBER: _ClassVar[int]
    PLAYERSCORES_FIELD_NUMBER: _ClassVar[int]
    updatedCells: _containers.RepeatedCompositeFieldContainer[UpdatedCell]
    removedSnakes: _containers.RepeatedScalarFieldContainer[str]
    playerScores: _containers.RepeatedCompositeFieldContainer[PlayerScore]
    def __init__(self, updatedCells: _Optional[_Iterable[_Union[UpdatedCell, _Mapping]]] = ..., removedSnakes: _Optional[_Iterable[str]] = ..., playerScores: _Optional[_Iterable[_Union[PlayerScore, _Mapping]]] = ...) -> None: ...

class GameStateMessage(_message.Message):
    __slots__ = ("updatedCells",)
    UPDATEDCELLS_FIELD_NUMBER: _ClassVar[int]
    updatedCells: _containers.RepeatedCompositeFieldContainer[UpdatedCell]
    def __init__(self, updatedCells: _Optional[_Iterable[_Union[UpdatedCell, _Mapping]]] = ...) -> None: ...

class UpdatedCell(_message.Message):
    __slots__ = ("address", "player", "foodValue")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    FOODVALUE_FIELD_NUMBER: _ClassVar[int]
    address: _containers.RepeatedScalarFieldContainer[int]
    player: str
    foodValue: int
    def __init__(self, address: _Optional[_Iterable[int]] = ..., player: _Optional[str] = ..., foodValue: _Optional[int] = ...) -> None: ...

class PlayerScore(_message.Message):
    __slots__ = ("playerName", "score", "snakes")
    PLAYERNAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    SNAKES_FIELD_NUMBER: _ClassVar[int]
    playerName: str
    score: int
    snakes: int
    def __init__(self, playerName: _Optional[str] = ..., score: _Optional[int] = ..., snakes: _Optional[int] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("playerName",)
    PLAYERNAME_FIELD_NUMBER: _ClassVar[int]
    playerName: str
    def __init__(self, playerName: _Optional[str] = ...) -> None: ...

class SubsribeRequest(_message.Message):
    __slots__ = ("playerIdentifier",)
    PLAYERIDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    playerIdentifier: str
    def __init__(self, playerIdentifier: _Optional[str] = ...) -> None: ...

class ServerUpdateMessage(_message.Message):
    __slots__ = ("messageType", "message")
    MESSAGETYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    messageType: MessageType
    message: str
    def __init__(self, messageType: _Optional[_Union[MessageType, str]] = ..., message: _Optional[str] = ...) -> None: ...

class EmptyRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
