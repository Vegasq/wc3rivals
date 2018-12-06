// <!DOCTYPE html>
// <html>
// <head>
//     <title></title>
//     <style type="text/css">
//         #region_select_menu {
//             background-color: red;
//         }
//         #region_select_menu div {
//             padding: 10px;
//             cursor: pointer;
//         }

class RegionSelector {
    // Provide <button> id to constructor

    constructor(button_id){
        var self = this;

        this.postfix_image = ' <img src="/static/images/down.svg">';

        this.closed_state = 0;
        this.open_state = 1;

        this.button_id = button_id;
        this.btn = document.getElementById(this.button_id);
        this.btn_text = document.getElementById(this.button_id + "_text");

        this.state = this.closed_state;

        this.vals = ["Europe", "US West", "US East"];
        this.ids = ["europe", "us_west", "us_east"];

        var parent_div = document.createElement("div");
        parent_div.style.position = "relative";
        parent_div.style.display = "inline";
        this.menu_div = document.createElement("div");
        parent_div.appendChild(this.menu_div);
        this.menu_div.style.display = "none";
        this.menu_div.style.position = "absolute";
        this.menu_div.setAttribute('id', 'region_select_menu');

        for (var i = this.vals.length - 1; i >= 0; i--) {
            let opt = document.createElement("div");
            opt.setAttribute('id', this.vals[i].split(" ").join("_").toLowerCase());
            opt.innerHTML = this.vals[i];
            opt.addEventListener("click", function(d){self.select_region(d);}, false);
            this.menu_div.appendChild(opt);
        }
        // document.body.appendChild(parent_div);
        var region_button = document.getElementById('region_button');
        region_button.parentNode.insertBefore(parent_div, region_button.nextSibling);

        this.btn_text.innerHTML = this.vals[0];
        this.btn.value = this.ids[0];
        this.btn.addEventListener("click", function(d){self.open_menu(d);}, false);

    }
    select_region(e){
        this.btn_text.innerHTML = e.target.innerHTML;
        this.btn.value = e.target.id;
        this.open_menu();
    }
    open_menu(e){
        // this.menu_div.style.top = (this.btn.offsetTop + this.btn.clientHeight) + "px";
        // this.menu_div.style.left = this.btn.offsetLeft + "px";

        if (this.state === this.closed_state){
            document.getElementById("region_select_menu").style.display = "block";
            this.state = this.open_state;
        } else if (this.state === this.open_state) {
            document.getElementById("region_select_menu").style.display = "none";
            this.state = this.closed_state;
        }
    }

}