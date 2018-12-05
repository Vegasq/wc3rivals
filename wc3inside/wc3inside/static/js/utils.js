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
    centrate_header();

    var inp = document.getElementById("search_input");
    var region = document.getElementById("region_button");
    var search_btn = document.getElementById("search_button");
   
    inp.addEventListener("keypress", function(e){
        console.log(e);
        var key = e.which || e.keyCode;
        if (key === 13) {
            search_emenies(inp.value, region.value);
        }
    });
    search_btn.addEventListener("click", function(e){
        console.log(e);
        search_emenies(inp.value, region.value);
    });

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