# Ephemeral Chat
A WebSocket chat app that allows users to create temporary profiles and group chats that are deleted when left.


This project was an outlet to learn more about web development and websockets, and I had a lot of fun working on it.
The idea was to create a chat app similar to discord that functions like omegle.


The front end was made with [tailwindcss](https://tailwindcss.com/) and jinja templating, while the backend server is written in python using [FastApi](https://fastapi.tiangolo.com/). The client side JavaScript establishes the websocket connection and handles the data being sent and recieved from and to the user.

### More Info
* There are ratelimits set in place to prevent spam and attacks.
* It is impossible to spoof your connection to act as another user.
* Anyone can create a room that anyone else can join using a shareable link. 
* Users can set their name, color, and avatar.
* The chat supports link previews and image previews.
* The chat natively supports any Discord emojis that are sent, and has a couple pre-picked emojis in it's emoji menu.
* The emoji menu is dynamic and adds new emojis that were sent in the chat into your emoji menu.
* The leader of the group is shown with a crown, which gets randomly passed to another user when they leave.
* Groups have a live member count.
 

### Screen Shots
<img src="https://cdn.discordapp.com/attachments/792686378366009354/863201239582900244/unknown.png" width=1000>
<img src="https://cdn.discordapp.com/attachments/792686378366009354/863201495645814814/unknown.png" width=1000>
<img src="https://cdn.discordapp.com/attachments/792686378366009354/863201858284683264/unknown.png" width=1000>
<img src="https://cdn.discordapp.com/attachments/792686378366009354/863202000673832980/unknown.png" width=1000>


