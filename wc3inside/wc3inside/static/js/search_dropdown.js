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

class SearchDropdown {
    // Provide <button> id to constructor

    constructor(button_id){
        var self = this;

        this.button_id = button_id;
        this.input = document.getElementById(this.button_id);


        var parent_div = document.createElement("div");
        parent_div.style.position = "relative";
        parent_div.style.display = "inline";
        this.menu_div = document.createElement("div");
        parent_div.appendChild(this.menu_div);
        this.menu_div.style.display = "none";
        this.menu_div.style.position = "absolute";
        this.menu_div.setAttribute('id', 'search_drop_down');

        this.input.parentNode.insertBefore(parent_div, this.input.nextSibling);

        // this.input.value = this.ids[0];
        this.input.addEventListener("focusout", function(d){
            var interval_id = setInterval(function(){
                self.close_menu();
                clearInterval(interval_id);
            }, 300);
        });

        this.input.addEventListener("keyup", function(d){
            self.close_menu();
            if (d.target.value.length >= 3) {

                do_get(
                    "/v1/usernames/"+get_current_gateway()+"/"+d.target.value,
                    function(d1){
                        var d1 = JSON.parse(d1);

                        for (var i = d1.length - 1; i >= 0; i--) {
                            let opt = document.createElement("div");

                            opt.innerHTML = "<a href='/u/"+get_current_gateway()+"/"+d1[i]+"'>" + d1[i] + "</a>";
                            self.menu_div.appendChild(opt);
                        }
                        self.input.parentNode.insertBefore(parent_div, self.input.nextSibling);
                        if (d1.length >= 1) {
                            self.open_menu();
                        } else {
                            self.close_menu();
                        }
                    }
                )
            }
        }, false);

    }
    open_menu(e){
        document.getElementById("search_drop_down").style.display = "block";
    }
    close_menu(){
        document.getElementById("search_drop_down").style.display = "none";
        this.menu_div.innerHTML = "";
    }

}