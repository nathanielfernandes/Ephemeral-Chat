const EVENT = "event";
const MESSAGE = "message";
const EPHEMERAL = "ephemeral";

const VALIDURL = /([a-z\-_0-9\/\:\.]*\.(jpg|jpeg|png|gif|webp))/gi
const DEFAULT_PFP = "https://cdn.discordapp.com/attachments/830269354649452564/863169775646670888/unknown.png";
const URL = /(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})/gi

const urlHost = window.location.host;
const urlParams = new URLSearchParams(window.location.search);
const clientUuid = urlParams.get('user');
const groupID = urlParams.get("group");

const messageClasses = ['bg-gray-700', 'rounded', 'py-1', 'mb-1'];
const userinfoClasses = ['flex', 'flex-row', 'items-center', 'py-1'];
const avatarClasses = ['rounded-full', 'h-8', 'w-8', 'mr-2', 'ml-3'];
const usernameClasses = ['font-medium', 'text-1xl'];
const timeClasses = ['font-thin', 'text-gray-400', 'ml-5', 'text-xs'];
const contentClasses = ['font-light', 'text-gray-100', 'ml-7', "flex", "flex-row"];
const interClasses = ['hover:bg-gray-600', 'rounded', 'duration-100', "space-y-1", "my-1"];

const imageClasses = ["rounded", "ml-7", "mb-1", "max-w-xs"];

const embedClasses = ["bg-gray-800", "px-3", "py-1", "rounded", "max-w-md", "w-max", "flex", "flex-none", "flex-wrap", "ml-7"];
const embedTitle = ["font-bold", "hover:underline", "text-xs"];
const embedDesc = ["text-gray-100", "text-xs"];
const embedImage = ["my-2", "max-w-min", "min-w-full", "rounded", "max-h-40", "flex", "items-center", "overflow-hidden"];


const crownClasses = ["fas", "fa-crown", "text-yellow-500"]

const eventClasses = ['bg-gray-700', 'text-center', 'hover:bg-gray-600', 'duration-100', 'rounded', 'py-1'];
const eventMessageClasses = ['font-light', 'text-sm', 'text-gray-300'];

const emojiButtonClasses = ["bg-gray-800", "hover:bg-gray-700", "duration-100", "rounded", "px-1", "py-1", "w-10", "h-10", "m-px", "items-center", "flex", "justify-center"];

const discomojiSettings = { "font-size": "20", "emoji-only-scale": 15 };



var knownEmojis = [
    "a:dogpog:860273780563509279",
    ":COOMER:849469772802686997",
    ":CS_BRUH:776544829768728617",
    ":pepe_cheer:830597372294725653",
    ":pepeheart:773419125464367115",
    ":wtf:796964193571176478",
    ":peek_ferret:855205013332295700",
    ":prayge:829726392320917584",
    ":rescepter:829887913592356875",
    ":rescepter2:834564847785476098",
    ":rescepter3:849503598537605130",
    ":rescepter4:835641282612822056",
    ":madge:807114360601575494",
    ":sus:829398037624389694",
    ":suspicious:804780162394357780",
    ":study:796934265601261568",
    ":AmongUsBlush:755565411252043889",
    ":FeelsClassyMan:622369279353946142",
    ":SCwtf:852024039962968084",
    ":Cat_Pat:836390600198062081",
    ":anguish:841196061598547968"
]




class ChatHandler {
    constructor(client_uuid, groupID) {
        this.client_uuid = client_uuid;
        this.groupID = groupID;
        this.messageInput = document.getElementById("messageInput");
        this.onlineMembers = document.getElementById("online-members");
        this.emojiMenu = document.getElementById("emoji-menu");
        this.chat = document.getElementById("chat");
        this.state = 1;
    }

    init() {
        this.ws = new WebSocket(`wss://${window.location.host}/ws/${this.groupID}/${this.client_uuid}`);
        this.ws.onerror = this.error;
        this.ws.onclose = this.close;
        this.ws.onmessage = this.onMessage;
        this.ws.ch = this;

        this.setupEmojis();
    }

    error() {
        window.location.replace("/?error=failed");
    }

    close() {
        window.location.replace("/?error=closed");
    }

    getTime() {
        var time = new Date();
        return time.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true })
    }

    getText(text) {
        return document.createTextNode(text);
    }

    isFresh(new_uuid) {
        var fc = this.chat.firstChild;
        try {
            var isFresh = (fc.getAttribute("client-uuid") == new_uuid);
        } catch (e) {
            isFresh = false;
        }
        return isFresh
    }

    addEmoji(element) {
        this.messageInput.value += "<" + element.firstChild.getAttribute("title") + ">";
    }

    toggleEmojis() {
        if (this.state == 1) {
            this.emojiMenu.style.display = "flex";
        } else {
            this.emojiMenu.style.display = "none";
        }
        this.state *= -1;
    }

    emojiError(emoji) {
        emoji.parentNode.style.display = 'none';
        emoji.style.display = 'none';
    }

    addEmojiToMenu(emoji) {
        var button = document.createElement("div");
        button.setAttribute("type", "button");
        button.setAttribute("onClick", "chathandler.addEmoji(this)");
        button.appendChild(this.getText("[" + emoji + "]"));
        emojiButtonClasses.forEach(_class => { button.classList.add(_class) });
        this.emojiMenu.appendChild(button);
        Discomoji.init(button, { "font-size": "30", "offsetY": "0px", "onError": "chathandler.emojiError(this)" });
    }


    setupEmojis() {
        var emojiMenu = document.getElementById("emoji-menu");
        knownEmojis.forEach(emoji => {
            var button = document.createElement("button");
            button.setAttribute("type", "button");
            button.setAttribute("onClick", "chathandler.addEmoji(this)");
            button.appendChild(this.getText("[" + emoji + "]"));
            emojiButtonClasses.forEach(_class => { button.classList.add(_class) });
            emojiMenu.appendChild(button);
        });
        Discomoji.init(emojiMenu, { "font-size": "30", "offsetY": "0px" });
    }

    discomojiSetup(content) {
        Discomoji.init(content, discomojiSettings);
        content.discomoji.emojisFound.forEach(emoji => {
            emoji = emoji[0].replace(BRACKETS, '')
            if (!knownEmojis.includes(emoji)) {
                knownEmojis.push(emoji);
                this.addEmojiToMenu(emoji)
            }
        });
    }

    pushMessage(json) {
        var fresh = this.isFresh(json.uuid)

        if (!fresh) {
            var space = "";
            var message = document.createElement('li');
            messageClasses.forEach(_class => { message.classList.add(_class) })

            var userinfo = document.createElement("span");
            userinfoClasses.forEach(_class => { userinfo.classList.add(_class) })

            var avatar = document.createElement("img");
            avatarClasses.forEach(_class => { avatar.classList.add(_class) })

            var username = document.createElement("p");
            usernameClasses.forEach(_class => { username.classList.add(_class) })
            username.classList.add(`text-${json.color}-400`);

            var time = document.createElement("p");
            timeClasses.forEach(_class => { time.classList.add(_class) })

            avatar.src = json.avatar;
            avatar.setAttribute("onerror", `this.src='${DEFAULT_PFP}'`);

            if (json.uuid === json.author) {
                var crown = document.createElement("i");
                crownClasses.forEach(_class => { crown.classList.add(_class) });
                username.appendChild(crown);
                space = ' ';
            }

            username.prepend(this.getText(json.username + space));

            time.appendChild(this.getText(this.getTime()));

            userinfo.appendChild(avatar);
            userinfo.appendChild(username);
            userinfo.appendChild(time);

            message.appendChild(userinfo);
        } else {
            var message = this.chat.firstChild;
        }

        var content = document.createElement("p");
        content.appendChild(this.getText(json.message));
        contentClasses.forEach(_class => { content.classList.add(_class) })

        content.innerHTML = content.innerHTML.replace(URL, `<a type="text" href="$1" target="blank" class="hover:underline px-1 text-${json.color}-400" >$1</a>`);

        var intermediate = document.createElement("div");
        intermediate.appendChild(content);
        interClasses.forEach(_class => { intermediate.classList.add(_class) });


        json.images.forEach(url => {
            var img = document.createElement("img");
            img.src = url;
            img.setAttribute("onerror", "this.style.display='none';");
            imageClasses.forEach(_class => { img.classList.add(_class) });
            intermediate.appendChild(img);
        })

        json.embeds.forEach(e => {
            var embed = document.createElement("div");
            embedClasses.forEach(_class => { embed.classList.add(_class) });
            embed.classList.add(`embed-color-${json.color}`);

            var info = document.createElement("div");
            info.classList.add("mr-2");

            var title = document.createElement("a");
            embedTitle.forEach(_class => { title.classList.add(_class) });
            title.appendChild(this.getText(e.title));
            title.classList.add(`text-${json.color}-400`);
            title.setAttribute("href", e.url);
            title.setAttribute("target", "blank");

            var desc = document.createElement("p");
            embedDesc.forEach(_class => { desc.classList.add(_class) })
            desc.appendChild(this.getText(e.description));

            info.appendChild(title);
            info.appendChild(desc);


            embed.appendChild(info);


            if (e.image) {
                var thumb = document.createElement("div");
                embedImage.forEach(_class => { thumb.classList.add(_class) });

                var thumbnail = document.createElement("img");
                thumbnail.src = e.image;
                thumbnail.setAttribute("onerror", "this.style.display='none';");

                thumb.appendChild(thumbnail);
                embed.appendChild(thumb);
            }

            intermediate.appendChild(embed);

        })

        message.appendChild(intermediate);

        if (!fresh) {
            message.setAttribute("client-uuid", json.uuid);
            this.chat.prepend(message);
        }

        this.discomojiSetup(content);

        return content;

    }

    pushEvent(json) {
        var event = document.createElement('li');
        eventClasses.forEach(_class => { event.classList.add(_class) });

        var eventMsg = document.createElement("p");
        eventMessageClasses.forEach(_class => { eventMsg.classList.add(_class) });

        eventMsg.appendChild(this.getText(`${json.username} ${json.message}`));
        event.appendChild(eventMsg);

        this.onlineMembers.innerText = json.online;
        this.chat.prepend(event);
    }

    pushEmepheralEvent(json) {
        var event = document.createElement('li');
        eventClasses.forEach(_class => { event.classList.add(_class) });

        var eventMsg = document.createElement("p");
        eventMessageClasses.forEach(_class => { eventMsg.classList.add(_class) });

        eventMsg.appendChild(this.getText(`${json.message}`));
        event.appendChild(eventMsg);

        this.chat.prepend(event);
    }


    onMessage(event) {
        var json = JSON.parse(event.data);
        if (json.type === MESSAGE) {
            var msg = this.ch.pushMessage(json);
            msg.scrollIntoView()
        } else if (json.type === EVENT) {
            this.ch.pushEvent(json);
        } else if (json.type === EPHEMERAL) {
            this.ch.pushEmepheralEvent(json);
        }
    }

    sendMessage(event) {
        this.ws.send(this.messageInput.value);
        this.messageInput.value = '';
        event.preventDefault()
    }
}

function copyClip(t) {
    var input = document.createElement('textarea');
    var text = t
    input.innerHTML = text
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    alert(text + " \ncopied to clip board!");
}

document.getElementById("chatID").innerText += ` ${groupID} `;
chathandler = new ChatHandler(clientUuid, groupID);
chathandler.init();


