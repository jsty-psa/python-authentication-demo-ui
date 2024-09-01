function eToNumber(num) {
    let sign = "";
    (num += "").charAt(0) == "-" && (num = num.substring(1), sign = "-");
    let arr = num.split(/[e]/ig);
    if (arr.length < 2) return sign + num;
    let dot = (.1).toLocaleString().substr(1, 1), n = arr[0], exp = +arr[1],
        w = (n = n.replace(/^0+/, '')).replace(dot, ''),
        pos = n.split(dot)[1] ? n.indexOf(dot) + exp : w.length + exp,
        L = pos - w.length, s = "" + BigInt(w);
    w = exp >= 0 ? (L >= 0 ? s + "0".repeat(L) : r()) : (pos <= 0 ? "0" + dot + "0".repeat(Math.abs(pos)) + s : r());
    L = w.split(dot); if (L[0] == 0 && L[1] == 0 || (+w == 0 && +s == 0)) w = 0; //** added 9/10/2021
    return sign + w;
    function r() { return w.replace(new RegExp(`^(.{${pos}})(.)`), `$1${dot}$2`) }
}

$(document).ready(function() {
    // alert("Hello World!")!
    $("button[id^='btn']").click(function(event) {
        event.preventDefault();
    });

    $("#btn-request-otp").click(function(event) {
        pcn = $("#individual_id").val();

        $.ajax({
            method: "GET",
            url: "/request/otp/" + pcn,
            success: function(data) {
                $("#authentication_response").val(data)
            }
        });
    });

    $("#btn-reset").click(function(event) {

    });

    $("#btn-submit").click(function(event) {
        individual_id = $("#individual_id").val();
        individual_id_type = $("#individual_id_type").val();
        
        input_bio = $("#input_bio").is(':checked') ? "on" : "off";
        input_otp = $("#input_otp").is(':checked') ? "on" : "off";
        input_demo = $("#input_demo").is(':checked') ? "on" : "off";
        input_ekyc = $("#input_ekyc").is(':checked') ? "on" : "off";

        input_otp_value = $("#input_otp_value").val();
        input_demo_value = $("#input_demo_value").val();

        $.ajax({
            method: "GET",
            url: "/authenticate/",
            data: {
                individual_id : individual_id,
                individual_id_type : individual_id_type,
                input_bio : input_bio,
                input_otp : input_otp,
                input_demo : input_demo,
                input_ekyc : input_ekyc,
                input_otp_value : input_otp_value,
                input_demo_value : input_demo_value,
            },
            success: function(data){
                console.log(data);
            }
        });
    });
});
