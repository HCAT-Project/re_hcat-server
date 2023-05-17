_This document is machine-translated by ChatGPT-3.5. 
If you find grammatical and semantic errors, and the document description is not clear, please PR or issue._

WARN: This document is not complete.

# Preface

> What kind of crappy document did I write last time! - hsn

In the server of version 1.x, we realized that direct read and write to the database would bring some unforeseeable problems, so hsn directly read and wrote to the database again (damn, let's change it next time~~). We also found that the imperfect database module caused logical confusion, so we wrote a new ~~still imperfect~~ database module and added some new features in version 2.x.

> What shit am I writing day after day!!!!!!!!! - hsn

The main purpose of this rewrite is to optimize the development process, reduce repetitive code, and improve development efficiency.

# Server Event

"Server Event" (referred to as "Event" in this section) is an important concept in the server, it is the entry point of the API or the specific implementation of certain methods.

## Base Event

`BaseEvent` is the base class of all events, it defines the basic attributes and methods of the events.

> uh..? How to use it? Stupid, just inherit it!!! - hsn

### Attributes

The `BaseEvent` class has the following attributes:

- `auth`: Indicates whether the event requires authentication, default is authentication enabled.
- `req`: The request object used by the Flask framework by default.
- `server`: Instantiated server class.
- `path`: The path when the user makes the request.
- `e_mgr`: Event Manager, used to run events.
- `user_id`: The user's ID, which must be logged in to obtain.

### Methods

The `BaseEvent` class has the following methods:

- `run()`: Runs the event, checks the integrity of the request parameters, and runs the `_run` function to process the logic.
- `_run()`: Specific event handling logic implementation.

## Event Creation

As mentioned above, just inherit it. But you also need to know the following:

### Naming of Events

- The naming of event files must conform to the [snake_case naming convention](https://en.wikipedia.org/wiki/Snake_case), for example, `test_event.py`.
- The naming of event classes must conform to the [UpperCamelCase naming convention](https://en.wikipedia.org/wiki/Camel_case), and must be the same as the file name.

### Authentication Mode

After creating the event, you need to set the authentication mode, that is, whether the event triggerer needs to log in. Enter `auth = True` or `auth = False` under the event.

```python
from src.event.base_event import BaseEvent


class TestEvent(BaseEvent):
    auth = True
```

### Entry Function

The entry function can only be `_run` function (generally), which is the specific implementation of the event. That is to say, when the event is triggered, the `_run` function will be called. The parameter of the `_run` function is the form submitted by the way (or the parameter of the get request).

```python
from src.event.base_event import BaseEvent
from src.containers import ReturnData


class TestEvent(BaseEvent):
    auth = True

    def _run(self, arg1, arg2="This is a default value"):
        print(arg1)
        print(arg2)
        return ReturnData(ReturnData.OK, "Hello World!")
```

## What are basic events? What are private events? What are auxiliary events?

Basic events refer to events that can be directly accessed in the browser and must be created in the `src/event/events` directory.

Private events are events that cannot be accessed directly in the browser and can only be called by other events. They can be created anywhere.

Auxiliary events are events that are called before another event is called. Auxiliary events must be created in the `src/event/auxiliary` directory and their filenames must start with `auxiliary_`.

### Creating Auxiliary Events

The process for creating auxiliary events is the same as for regular events, but the `main_event` property must be set and the value of the `main_event` property must be an event class.

```python
from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.event.events.chat.send_group_msg import SendGroupMsg


class ThisIsAnAuxiliaryEvent(BaseEvent):
    auth = True
    main_event = SendGroupMsg

    def _run(self, arg1, arg2="This is a default value"):
        print(arg1)
        print(arg2)
        return False, ReturnData(ReturnData.OK, "Hello World!")
```

Oh, what is that Boolean value returned? That is whether to cancel the event or not, that is, whether to not run the main event.

However, thanks to some effort by hsn, you can return a Boolean and ReturnData, only ReturnData, or only Boolean.

> hsn: What kind of effort? Just a little type checking... - hsn

If you do not return a Boolean, it defaults to not canceling the event.

# User Class

The User class is a class for users that implements basic user functions such as verification, password modification, and so on.

## Untitled Chapter

For convenience, hsn uses `pickle` for data storage (bad practice!), but...

> hsn: Hey?! Why aren't the class variables automatically added after the function code is updated?
>
> : A certain someone hasn't realized that pickle load does not run __init__.

So:
The User class inherits from the Jelly class--a class created to assist with pickle load for class variable updates.

## Members

- `todo_list`: A list of to-do items, type list
- `token`: User token, type string
- `status`: User status, type string
- `friend_dict`: User's friend dictionary, type dictionary
- `groups_dict`: User's group dictionary, type dictionary
- `email`: User's email, type string
- `language`: User's language, type string
- `user_name`: User's username, type string
- `user_id`: User's ID, type string
- `salt`: User's `salt`, type string

# Group Class

The Group class represents a group in a chat application, including basic group information, member management, and event broadcasting.
> Well, as you guessed, the Group class also inherits from the Jelly class. - hsn

## Properties

- `id`: Group ID, type string
- `name`: Group name, type string
- `member_dict`: Group member dictionary, type dictionary, key is user ID, value is user object
- `owner`: Group owner user ID, type string
- `admin_list`: Admin user ID set, type set
- `member_settings`: Member settings dictionary, type dictionary, key is user ID, value is member setting object
- `ban_dict`: Banned member dictionary, type dictionary, key is user ID, value is ban object
- `group_settings`: Group settings dictionary, type dictionary, containing validation method, question, answer,
