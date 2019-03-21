<template>
    <div id="app">
        <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
        <Config :keys="userconfig" />
        <FileViewer :contents="currentFile" />
        <FilePermissionsViewer :contents="currentFile" />
        <div class="top-bar">
            <!-- <h4  contenteditable="true" class="username" v-model="username">{{ username }}</h4> -->
            <input type="text" class="pword-input" name="" v-model="username">
            <input type="text" class="pword-input" name="" v-model="password">
        </div>
        <div class="main">
            <div class="cent">
                <NucidBar query="" />
            </div>
            <div class="contain">
                <div class="left-pane">
                    <h4>My Friends</h4><br>
                    <a class="clickables" @click="addContact">➕</a>
                    <!-- <button @click="addContact">➕</button> -->
                    <Contacts :people="mycontacts" />
                </div>
                <!-- <button @click="addContact">Add</button> -->
                <div class="center-console">
                    <vue-dropzone ref="myVueDropzone" id="dropzone" v-on:vdropzone-sending="sendingEvent" v-on:vdropzone-success="uploadComplete" :options="dropzoneOptions" style="display:none;"></vue-dropzone>
                    <Files :files="myfiles" />
                </div>
                <!-- <button @click="addContact">Grant</button> -->
                <div class="right-pane">
                    <h4>Add A File</h4><br>
                    <a class="clickables" @click="toggleDropzone">💾</a>
                    <!-- <br /> -->
                    <!-- <br /> -->
                    <!-- <h4>My Keys</h4><br> -->
                    <!-- <a class="clickables" @click="openConfig">🔐</a> -->
                </div>
            </div>
        </div>
    </div>
</template>
<script>
// import HelloWorld from './components/HelloWorld.vue'

import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'

import $ from 'jquery';

import NucidBar from './components/NucidBar.vue'
import Files from './components/Files.vue'
import Contacts from './components/Contacts.vue'
import Config from './components/Config.vue'
import FileViewer from './components/FileViewer.vue'
import FilePermissionsViewer from './components/FilePermissionsViewer.vue'

export default {
    name: 'app',
    data: function() {
        return {
            // myname: ,
            mycontacts: [],
            currentFile: "",
            userconfig: [],
            myfiles: [],
            // username: "happyfeet",
            username: "",
            // password: "qwertyuiopqwertyuiop",
            password: "",
            dropzoneOptions: {
                url: 'http://localhost:5000/data',
                thumbnailWidth: 150,
                maxFilesize: 100.0,
                // headers: ,
            },
        }
    },
    components: {
        // HelloWorld
        vueDropzone: vue2Dropzone,
        NucidBar,
        Files,
        FileViewer,
        FilePermissionsViewer,
        Contacts,
        Config
    },
    methods: {
        updateCurrentFile: function() {
            this.currentFile = "davud";
        },
        sendingEvent(file, xhr, formData) {

            console.log(this.username, this.password)

            // console.log(file)
            formData.append("username", this.username)
            formData.append("password", this.password)
            formData.append("filename", file.name)
            // formData.append("contents", "hello world! this is a rest request 2")

            // formData.append('paramName', 'some value or other');
        },
        grantAccess(recipient_name, user, pass, cid, fname, enc, sig) {

            // console.log({
            //     "username": user,
            //     "password": pass,
            //     "cid": cid,
            //     "filename": fname,
            //     "enc": enc,
            //     "sig": sig,
            // })

            var data = JSON.stringify({
                "username": user,
                "password": pass,
                "cid": cid,
                "filename": fname,
                "enc": enc,
                "sig": sig,
            })

            console.log(data)

            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "http://127.0.0.1:5000/allow_access",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": data
            }

            $.ajax(settings).done(function(response) {
                console.log(response);

                var files = this.$parent.files

                var file = files.filter(function(el) {
                    return el.cid == cid
                })[0];

                file.granted_access.push({ "user": recipient_name, "allower": user, "nucid": response["nucid"] })


                console.log(file)

            }.bind(this));



        },
        uploadComplete(file, response) {

            console.log(response)


            var nucid = response["nucid"]
            var settings = {
                "async": true,
                "crossDomain": true,
                "url": "http://127.0.0.1:5000/decrypt_message",
                "method": "POST",
                "headers": {
                    "content-type": "application/json"
                },
                "processData": false,
                "data": JSON.stringify({
                    "username": this.username,
                    "nucid": nucid
                })
            }

            var info = nucid.split("//")[1].split("_");
            console.log(info)
            $.ajax(settings).done(function(response) {

                // console.log("compeltedUpload",response);

                this.$parent.files.push({

                    "label": info[3],
                    "cid": info[0],
                    "contents": response["contents"],
                    "size": response["contents"].length,
                    "granted_access": [
                        { "user": this.username, "allower": this.username, "nucid": nucid }
                    ]

                })

                // {
                //     "label": "art.png",
                //     "cid": "QmWadaT...",
                //     "contents": null,
                //     "size": 18
                // }
            }.bind(this));

            // e.preventDefault();



            // formData.append('paramName', 'some value or other');
        },
        toggleDropzone: function() {
            if (document.getElementById("dropzone").style.display != "block") {
                document.getElementById("dropzone").style.display = "block"
            } else {
                document.getElementById("dropzone").style.display = "none"
            }

        },
        updateContacts: function() {
            this.mycontacts = this.$parent.contacts
        },
        updateFiles: function() {
            this.myfiles = this.$parent.files
        },
        updateConfig: function() {
            this.userconfig = this.$parent.user //[this.$parent.user.roles.alice.pub.root]
        },
        addContact: function() {
            this.$parent.contacts.push({
                "name": "richard",
                "pub": {
                    "root": "",
                    "signing": ""
                }
            })
        },
        openConfig: function() {
            // need better way to call Config method
            this.$children[0].toggleConfig()
            // console.log()
        }
    },
    created: function() {
        /* eslint-disable no-console */
        this.updateContacts()
        this.updateConfig()
        this.updateFiles()
    }
}
</script>
<style>
.pword-input {
    border-radius: 5px;
    padding: 5px;
    margin: 5px;
}

.top-bar {

    display: -webkit-inline-box;
    /*background: #43cbf2;*/
    background: #085fcc;
    height: 36px;
    text-align: left;
    top: 0;
    left: 0;
    right: 0;
    position: absolute;
}

.username {
    color: #fff;
    margin: 10px;
}

th {
    color: #085fcc !important;
}

h4 {
    color: #aaa;
}

#app {

    padding-top: 60px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    font-family: 'Montserrat', sans-serif;

}

.left-pane {
    width: 100px;
    left: 18%;
    top: 15%;
    list-style-type: none;
}

.right-pane {
    width: 100px;
    right: 18%;
    top: 15%;
    list-style-type: none;
}

.contain {
    display: -webkit-inline-box;
}

.clickables {
    font-size: 16pt;
}

.clickables:hover {
    font-size: 18pt;
}
</style>