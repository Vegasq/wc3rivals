function centrate_header (){
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
    var headerHeight = document.getElementsByTagName("header")[0].offsetHeight;

    var middleOfTheScreen = y/2;
    var headerPosition = middleOfTheScreen - (headerHeight/2);
    document.getElementsByTagName("header")[0].style.paddingTop = headerPosition+"px";
}

function on_search() {
    document.getElementById("enemies_table").style.display = "table";
    document.getElementById("footer").style.display = "table";
    document.getElementsByTagName("header")[0].style.paddingTop = "30px";

}
function on_load() {
    document.getElementById("enemies_table").style.display = "none";
    document.getElementById("footer").style.display = "none";
    new RegionSelector("region_button");
    centrate_header();

    let dbstate = new DBState();
    dbstate.start();


    var inp = document.getElementById("search_input");
    var region = document.getElementById("region_button");
    var search_btn = document.getElementById("search_button");
   
    inp.addEventListener("keypress", function(e){
        var key = e.which || e.keyCode;
        if (key === 13) {
            search_emenies(inp.value, region.value);
        }
    });
    search_btn.addEventListener("click", function(e){
        search_emenies(inp.value, region.value);
    });


    if (window.location.href.indexOf("/u/") !== -1){
        var q = window.location.href.split("/u/")[1].split("/");
        var username = q[1];
        var gateway = q[0];

        document.getElementById("search_input").value = username;
        document.getElementById("region_button").value = gateway;

        search_emenies(username, gateway);
    }

}
function search_emenies(username, gateway){
    let os = new Enemies(username, gateway);
    os.start();
}

function do_get(url, report_to) {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.responseType = 'text';

    xhr.onload = function () {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                report_to(xhr.responseText);
            }
        }
    };

    xhr.send(null);
}

function render_template(template_id, vars){
    var tpl = document.getElementById(template_id).innerHTML;
    var tag_re = /{\s*[a-z_]*\s*}/gm;
    var we_have_tag = true;

    var max_errors = 10;

    for (var i = 0; we_have_tag == true; i--) {
        var some_tag = tag_re.exec(tpl);

        if (some_tag === null){
            if (tpl.indexOf("{") === -1) {
                we_have_tag = false;
                break;
            }
            max_errors -= 1;
            if (max_errors === 0) {
                break;
            }
            continue;
        }
        var key_name = some_tag[0].split(" ").join();
        key_name = key_name.replace("{", "");
        key_name = key_name.replace("}", "");

        tpl = tpl.split(some_tag[0]).join(vars[key_name]);
    }
    return tpl;
}

