<script>
export default {
    data: function() {
        return {
            current_gateway: "europe",
            gateway_dropdown_active: false,
            search_dropdown_active: false,
            gw_id_to_name: {
                'europe': 'Europe',
                'us_west': 'US West',
                'us_east': 'US East'
            },
            search_input: "",
            redirect_to_single: false
        }
    },
    methods: {
        activate_gateway_dropdown: function(){
            if (this.gateway_dropdown_active){
                this.gateway_dropdown_active = false;
            } else {
                this.gateway_dropdown_active = true;
            }
        },
        select_region: function(event){
            if (event.hasOwnProperty('toElement')) {
                this.current_gateway = event.toElement.id;
            } else {
                // FireFox
                this.current_gateway = event.target.id;
            }
            this.activate_gateway_dropdown();
        },
        close_search_dropdown: function(){
            var self = this;
            var interval_id = setInterval(function(){
                self.search_dropdown_active = false;
                clearInterval(interval_id);
            }, 300);
        },
        onsearchinput: function(event){
            if (this.search_input.length <= 3) {
                return;
            }
            if (event.which == 13) {
                this.redirect_to_single = true;
                this.api_call();
            } else {
                this.redirect_to_single = false;
                this.api_call(false);
                this.search_dropdown_active = true;
            }
        },
        search_button_pressed: function(){
            this.redirect_to_single = true;
            this.api_call();
            this.search_dropdown_active = true;
        },
        api_call: function(){
            this.$store.dispatch(
                'getUsernames',
                {'gateway': this.current_gateway,
                 'username': this.search_input.toLowerCase()});
        },
    },
    watch: {
        usernames: function(){
            if (this.redirect_to_single === true && this.usernames.length === 1){
                this.search_dropdown_active = false;
                this.$router.push({'name': 'rivals', 'params': {
                    'gateway': this.current_gateway, username: this.usernames[0]}});
            }
        }
    },
    computed: {
        usernames: function(){
            return this.$store.getters.getUsernames;
        }
    },
}
</script>

<template>
    <header>
        <router-link :to="{ name: 'main'}">
            <img class="header_logo" src="../assets/logo-small-warcraft3.png">
            <span class="header_wc3">WC3</span>
            <span class="header_inside">RIVALS</span>
        </router-link>
        <img class="glass_icon" src="../assets/glass.svg"><input id="search_input" v-model="search_input" v-on:keyup="onsearchinput" v-on:focusout="close_search_dropdown" placeholder="e.g. FollowGrubby">
        <div id="search_dropdown" v-if="search_dropdown_active">
            <div id="search_drop_down">
                <div v-for="player in usernames" :key="player">
                    <router-link :to="{ name: 'rivals', params: {gateway: current_gateway, username: player}}">
                        <div>{{ player }}</div>
                    </router-link>
                </div>
                <div v-if="usernames.length == 0">
                    Not found
                </div>
            </div>
        </div>

        <button id="region_button" v-on:click="activate_gateway_dropdown()">
            <b id="region_button_text">{{ gw_id_to_name[current_gateway] }}</b> 
            <img src="../assets/down.svg">
        </button>

        <div id="select_region">
            <div v-if="gateway_dropdown_active">
                <div v-on:click="select_region" id="europe">Europe</div>
                <div v-on:click="select_region" id="us_west">US West</div>
                <div v-on:click="select_region" id="us_east">US East</div>
            </div>
        </div>

        <button id="search_button" v-on:click="search_button_pressed">Search</button>
    </header>
</template>



<style scoped>
header {
    padding-top: 30px;
    padding-bottom: 50px;
}
header > a {
    text-decoration: none;
}
header .header_logo {
    width: 40px;
    height: 40px;
    position: relative;
    top: 7px;
    padding-right: 10px;
}
header .header_wc3 {
    font-weight: bold;
    width: 208px;
    height: 40px;
    font-family: Roboto;
    font-size: 40px;
    font-style: normal;
    font-stretch: normal;
    line-height: 1;
    letter-spacing: normal;
    color: #ffffff;
}
header .header_inside {
    width: 208px;
    height: 40px;
    font-family: Roboto;
    font-size: 40px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: 1;
    letter-spacing: normal;
    color: #ffffff;
}
header #search_input {
    width: 235px;
    height: 40px;
    border-radius: 4px;
    background-color: rgba(216, 216, 216, 0.15);
    border: 0;
    color: #f0f0f0;
    font-size: 16px;
    margin-left: 20px;
    position: relative;
    top: -8px;
    padding-left: 45px;
    outline: none;
    left: -20px;
    margin-right: 2px;
}
header .glass_icon {
    position: relative;
    left: 35px;
    top: -4px;
}
header #search_button {
    width: 100px;
    height: 40px;
    border-radius: 4px;
    background-color: #ffffff;
    font-family: Roboto;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #ea760e;
    outline: none;
    position: relative;
    top: -9px;
    left: 3px;
    cursor: pointer;
}

header #region_button {
    width: 110px;
    height: 40px;
    border-radius: 4px;
    background-color: #ffffff;
    font-family: Roboto;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #ea760e;
    outline: none;
    position: relative;
    top: -9px;
    right: 10px;
    cursor: pointer;
    text-align: left;
    padding: 0 10px;
}
header #region_button img {
    position: relative;
    top: 2px;
    float: right;
}

#select_region > div {
    width: 70px;
    border-radius: 4px;
    background-color: #ffffff;
    font-family: Roboto;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #4a4a4a;
    outline: none;
    right: 10px;
    cursor: pointer;
    padding: 0px 20px 10px 20px;
    margin-top: 10px;

    position: absolute;
    top: 18px;
}

#select_region > div::before {
    display: block;
    width: 10px;
    height: 10px;
    background-color: white;
    content: "";
    top: -4px;
    position: relative;
    left: 67px;
    transform: rotate(45deg);
}
#select_region > div div {
    line-height: 25px;
}
#select_region > div div:hover {
    color: #ea760e;
}


#search_drop_down {
    width: 235px;
    border-radius: 0 0 4px 4px;
    background-color: #ffffff;
    font-family: Roboto;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #4a4a4a;
    outline: none;
    right: 25px;
    cursor: pointer;
    padding: 10px 20px 10px 20px;
    margin-top: -7px;
    position: absolute;
    z-index: 1;
}

#search_drop_down > div {
    line-height: 30px;
    height: 30px;
    /* border: 1px solid red; */
}
#search_drop_down > div > div {
    width: 100%;
    height: 100%;
}
#search_drop_down a {
    text-decoration: none;
    color: #4a4a4a;
}
#search_drop_down a:hover {
    color: #ea760e;
}

div#select_region, div#search_dropdown {
    position: relative;
    display: inline;
    z-index: 1;
}
div#select_region > div, div#search_dropdown > div {
    position: absolute;
}

</style>
