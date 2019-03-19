vm = new Vue({
    el: '#app',

    data: {
        isError: false,
        nucypher_network: "localhost:11500",
        ipfs_api_gateway: "https://ipfs.infura.io:5001",
        local_user_directory: "",
        files: [],
        dfiles: [],
        checkedFiles: [],
        isConnected: false,
        repc_keys: null,
        sharables: [],
        isLoggedIn: false,
        users: [],
        testingCode: "1234",
    },
    methods: {
        get_recpient_keys: function() {
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/get_user_keys",
                "method": "GET",
                "headers": {}
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                this.repc_keys = JSON.parse(response)

            }.bind(this));

        },
        skipSelect: function(){
            document.getElementById("logger").style.display = "none";
            document.getElementById("log-spinner").style.display = "block";
            document.getElementById("login-overlay").style.display = "none";
        },
        selectUser: function(e) {

            document.getElementById("logger").style.display = "none";
            document.getElementById("log-spinner").style.display = "block";
            // document.getElementById("step1").style.border = "solid red";


            value = e.target.textContent.trim();
            value = value + "/"
            this.local_user_directory = value

            console.log(value)

            data = JSON.stringify({
                "directory": this.local_user_directory,
            })

            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/login_as_sender",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                document.getElementById("login-overlay").style.display = "none";
                this.isLoggedIn = true

                this.get_recpient_keys()
            }.bind(this));
            console.log(e.target)

        },
        get_server_users: function() {
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/get_server_users",
                "method": "GET",
                "headers": {}
            }

            $.ajax(settings).done(function(response) {
                console.log(response);
                this.users = JSON.parse(response)

            }.bind(this));
        },
        decrypt_file: function() {


            ipfs_hash = document.getElementById("d_ipfs_hash").value
            policy_key = document.getElementById("d_policy_key").value
            sign_key = document.getElementById("d_sign_key").value
            label = document.getElementById("d_label").value

            // ipfs_hash = "QmW7Euib4RuYurZ3Fpvxbiw4WUWm988svY99Ji7MT7aZfM"
            // policy_key = "AscpZgmJQzFm3qm4R9Zcr0aD12lXFLN91oYFyXqI0lPy"
            // sign_key = "Ao3MByd5KhDHZn22naPZMnGIZlF1MKRSdrkmLoSz3Vr1"
            // label = "name"


            data = JSON.stringify({
                "policy": [
                    ipfs_hash,
                    policy_key,
                    sign_key,
                    label,
                ]
            })

            console.log(data)
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/decrypt_message",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                data = JSON.parse(response);

                // this.dfiles.push({
                //     "name": label,
                //     "type": data["message"],
                //     "ipfshash": ipfs_hash,
                //     "size": "-",
                //     "tag": "dev"
                // })

                this.get_dfiles()




            }.bind(this));
        },
        greet: function(event) {
            // `event` is the native DOM event
            alert(event.target.tagName)
        },
        grant_access: function() {


            for (let o of this.checkedFiles) {

                console.log(o)
                console.log(this.files)
                console.log(this.files.filter(file => file.name == o))

                o = this.files.filter(file => file.name == o)[0]

                label = o.name
                hash = o.ipfshash

                enc = document.getElementById("enc_pubkey").value
                sig = document.getElementById("sig_pubkey").value

                payload = {
                    "label": label,
                    "enc_pubkey": enc,
                    "sig_pubkey": sig,
                    "cid": hash
                }
                console.log(payload)
                data = JSON.stringify(payload)

                var settings = {
                    "async": true,
                    "crossDomain": true,
                    "url": "/allow_access",
                    "method": "POST",
                    "headers": {
                        "content-type": "application/json"
                    },
                    "processData": false,
                    "data": data
                }

                $.ajax(settings).done(function(response) {
                    console.log(response);

                    this.sharables.push(JSON.parse(response))
                }.bind(this));

                // console.log(payload)
                // expected output: 1

                // break; // closes iterator, triggers return
            }
            // console.log("e")

            // e.preventDefault();

        },
        get_files: function() {
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/get_files",
                "method": "GET",
                "headers": {}
            }

            $.ajax(settings).done(function(response) {
                // console.log(response);
                this.files = JSON.parse(response)
                console.log(this.files)

                // this.$forceUpdate()

            }.bind(this));
        },
        get_dfiles: function() {
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/get_dfiles",
                "method": "GET",
                "headers": {}
            }

            $.ajax(settings).done(function(response) {
                // console.log(response);
                this.dfiles = JSON.parse(response)
                console.log(this.dfiles)

                // this.$forceUpdate()

            }.bind(this));
        },
        submit: function(e) {
            // label = e.target.querySelectorAll("input")[0].value
            label = e.target.querySelector("input").value
            contents = e.target.querySelector("textarea").value
            // contents = e.target.querySelectorAll("input")[1].value
            data = JSON.stringify({
                "label": label,
                "contents": contents
            })
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/add_data",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                this.get_files()
            }.bind(this));

            // console.log(data)
        },
        addNewUser: function(e) {

            
            document.getElementById("logger").style.display = "none";
            document.getElementById("log-spinner").style.display = "block";
            // document.getElementById("step1").style.border = "solid red";


            value = e.target.value.trim();
            value = value + "/"
            this.local_user_directory = value

            console.log(value)

            data = JSON.stringify({
                "directory": this.local_user_directory,
            })

            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/login_as_sender",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);


                document.getElementById("login-overlay").style.display = "none";
                this.isLoggedIn = true

                this.get_recpient_keys()
            }.bind(this));
            console.log(e.target)
        },
        changeLocalUser: function(e) {
            value = e.target.value;
            targ = e.target.id

            this[targ] = value

            console.log(value)


            data = JSON.stringify({
                "directory": this.local_user_directory,
            })

            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/login_as_sender",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                document.getElementById("login-overlay").style.display = "none";
                this.isLoggedIn = true

                this.get_recpient_keys()
            }.bind(this));

        },
        updateConnection: function(e) {


            value = e.target.value;
            targ = e.target.id

            this[targ] = value

            data = JSON.stringify({
                "nucypher_network": this.nucypher_network,
                "ipfs_api_gateway": this.ipfs_api_gateway
            })

            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "/connect",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                this.isConnected = true
            }.bind(this));

            console.log("redo network connect")
        },
        copyTestingCode(e) {

            // value = e.target.textContent
            value = e.target.getAttribute("value")

            var tempInput = document.createElement("input");
            tempInput.style = "position: absolute; left: -1000px; top: -1000px";
            tempInput.value = value;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand("copy");
            document.body.removeChild(tempInput);
        },
    },
    created() {
        // this.todo()
        this.get_server_users()

        this.get_files()
        this.get_dfiles()

        data = JSON.stringify({
            "nucypher_network": this.nucypher_network,
            "ipfs_api_gateway": this.ipfs_api_gateway
        })

        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "/connect",
            "method": "POST",
            "headers": {
                "content-type": "application/json"
            },
            "processData": false,
            "data": data
        }

        $.ajax(settings).done(function(response) {
            console.log(response);

            this.isConnected = true
        }.bind(this));

        this.get_recpient_keys()

        // this.updateConnection()
        // this.changeLocalUser()
    }
});



function grant_access_raw() {
    vm.grant_access()
}

function decrypt_file_raw() {
    vm.decrypt_file()
}


var ui = $(".ui"),
    sidebar = $(".ui__sidebar"),
    main = $(".ui__main"),
    uploadDrop = $(".upload-drop");

// SIDEBAR TOGGLE
$(".sidebar-toggle").on("click", function(e) {
    e.preventDefault();
    ui.toggleClass("ui__sidebar--open");
});

// MODAL
$("[data-modal]").on("click", function(e) {
    e.preventDefault();
    var target = $(this).data("modal");
    openModal(target);
});

function openModal(id) {
    $("#" + id).toggleClass("info-modal--active");
    $('[data-modal="' + id + '"]').toggleClass("ui__btn--active");
}

// OVERLAY
$("[data-overlay]").on("click", function(e) {
    e.preventDefault();
    var target = $(this).data("overlay");
    openOverlay(target);
});

// Close Overlay on Overlay Background Click
$(".overlay").on("click", function(e) {
    if (e.target !== e.currentTarget) return;
    closeOverlay();
});

$(".overlay__close").on("click", function(e) {
    closeOverlay();
});

function openOverlay(id) {
    $("#" + id + ".overlay").addClass("overlay--active");
}

function closeOverlay() {
    $(".overlay--active").removeClass("overlay--active");
}

// File Tree
$(".folder").on("click", function(e) {
    var t = $(this);
    var tree = t.closest(".file-tree__item");

    if (t.hasClass("folder--open")) {
        t.removeClass("folder--open");
        tree.removeClass("file-tree__item--open");
    } else {
        t.addClass("folder--open");
        tree.addClass("file-tree__item--open");
    }

    // Close all siblings
    tree
        .siblings()
        .removeClass("file-tree__item--open")
        .find(".folder--open")
        .removeClass("folder--open");
});

// DRAG & DROP
var dc = 0;
uploadDrop
    .on("dragover", function(e) {
        dc = 0;
        drag($(this), e);
    })
    .on("dragenter", function(e) {
        drag($(this), e);
        dc++;
    })
    .on("dragleave", function(e) {
        dragend($(this), e);
        dc--;
    })
    .on("drop", function(e) {
        drop($(this), e);
    });

function drag(that, e) {
    e.preventDefault();
    e.stopPropagation();
    that.addClass("upload-drop--dragover");
}

function dragend(that, e) {
    e.preventDefault();
    e.stopPropagation();
    if (dc === 0) {
        $(".upload-drop--dragover").removeClass("upload-drop--dragover");
    }
}

function drop(that, e) {
    dc = 0;
    dragend($(this), e);
    // Handle file
    alert("It seems you dropped something!");
}

// SORTING
function sortTable(n, method) {
    var table,
        rows,
        switching,
        i,
        x,
        y,
        shouldSwitch,
        dir,
        switchcount = 0;
    table = document.getElementById("file-table");
    switching = true;
    dir = "asc";

    while (switching) {
        switching = false;
        rows = table.getElementsByTagName("tr");

        for (i = 1; i < rows.length - 1; i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[n];
            y = rows[i + 1].getElementsByTagName("td")[n];

            if (method == "123") {
                if (dir == "asc") {
                    if (parseFloat(x.innerHTML) > parseFloat(y.innerHTML)) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) {
                        shouldSwitch = true;
                        break;
                    }
                }
            } else {
                if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}