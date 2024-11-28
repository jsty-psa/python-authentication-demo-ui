$(function() {
    const ids = {
        "firstName": "firstName",
        "lastName": "lastName",
        "middleName": "middleName",
        "name": "name",
        "gender": "gender",
        "emailId": "emailId",
        "phoneNumber": "phoneNumber",

        "age": "age",
        "bloodType": "bloodType",
        "maritalStatus": "maritalStatus",
        "dob": "dob",
        "postalCode": "postalCode",
        "pobProvince": "pobProvince",
        "pobCity": "pobCity",

        "residenceStatus": "residenceStatus",
        "presentCity": "presentCity",
        "presentBarangay": "presentBarangay",
        "presentProvince": "presentProvince",
        "presentAddress": "presentAddress",
        "presentAddressLine1": "presentAddressLine1",
        "fullAddress": "fullAddress",

        "permanentProvince": "permanentProvince",
        "permanentAddress": "permanentAddress",
        "permanentFullAddress": "permanentFullAddress",
        "permanentCity": "permanentCity",
        "permanentZipcode": "permanentZipcode",
        "permanentBarangay": "permanentBarangay",
        "permanentAddressLine1": "permanentAddressLine1",
    };

    
    const demog_id_value = {
        "firstName": false,
        "lastName": false,
        "middleName": false,
        "name": false,
        "gender": false,
        "emailId": false,
        "phoneNumber": false,

        "age": false,
        "bloodType": false,
        "maritalStatus": false,
        "dob": false,
        "postalCode": false,
        "pobProvince": false,
        "pobCity": false,

        "residenceStatus": false,
        "presentCity": false,
        "presentBarangay": false,
        "presentProvince": false,
        "presentAddress": false,
        "presentAddressLine1": false,
        "fullAddress": false,

        "permanentProvince": false,
        "permanentAddress": false,
        "permanentFullAddress": false,
        "permanentCity": false,
        "permanentZipcode": false,
        "permanentBarangay": false,
        "permanentAddressLine1": false,
    };
    
    const id_label = {
        "firstName": "First Name",
        "lastName": "Last name",
        "middleName": "Middle Name",
        "name": "Full Name",
        "gender": "Gender",
        "emailId": "Email Address",
        "phoneNumber": "Mobile Number",

        "age": "Age",
        "bloodType": "bloodType",
        "maritalStatus": "Martial Status",
        "dob": "Date of Birth",
        "postalCode": "Postal Code",
        "pobProvince": "Place of Birth (Province)",
        "pobCity": "Place of Birth (City)",

        "residenceStatus": "Residence Status",
        "presentCity": "Present Address (City)",
        "presentBarangay": "Present Address (Barangay)",
        "presentProvince": "Present Address (Province)",
        "presentAddress": "Present Address (House Number)",
        "presentAddressLine1": "Present Address (House Number din ata?)",
        "fullAddress": "Present Address (Full Address)",

        "permanentProvince": "Permanent Address (Province)",
        "permanentAddress": "Permament Address (Home Number)",
        "permanentFullAddress": "Permament Address (Full Address)",
        "permanentCity": "Permanent Address (City)",
        "permanentZipcode": "Permanent Address (Zip Code)",
        "permanentBarangay": "Permanent Address (Barangay)",
        "permanentAddressLine1": "Permament Address (Home Number din ata?)",
    };
    
    const category_contents = {
        1: [
            "firstName",
            "lastName",
            "middleName",
            "name",
            "gender",
            "emailId",
            "phoneNumber",
        ],

        2: [
            "age",
            "bloodType",
            "maritalStatus",
            "dob",
            "postalCode",
            "pobProvince",
            "pobCity",
        ],

        3: [
            "residenceStatus",
            "presentCity",
            "presentBarangay",
            "presentProvince",
            "presentAddress",
            "presentAddressLine1",
            "fullAddress",
        ],

        4: [
            "permanentProvince",
            "permanentAddress",
            "permanentFullAddress",
            "permanentCity",
            "permanentZipcode",
            "permanentBarangay",
            "permanentAddressLine1",
        ],
    };

    disableFingerPrintForm(true);
    disableIrisForm(true);
    disableFaceForm(true);
    disableOTPForm(true);
    disableDemographicForm(true);
    hideDemographicInputCategory();

    $("#category_page1").click(function() {
        hideDemographicInputCategory();
        $("#modal-demog-input-category-1").show();
        setActiveCategory('category_page1');
    });

    $("#category_page2").click(function() {
        hideDemographicInputCategory();
        $("#modal-demog-input-category-2").show();
        setActiveCategory('category_page2');
    });

    $("#category_page3").click(function() {
        hideDemographicInputCategory();
        $("#modal-demog-input-category-3").show();
        setActiveCategory('category_page3');
    });

    $("#category_page4").click(function() {
        hideDemographicInputCategory();
        $("#modal-demog-input-category-4").show();
        setActiveCategory('category_page4');
    });

    $("#model-demog-input-save").click(function() {
        var demog_result_id = 1;

        $("div[id^=demog-result-]").html("");

        $.each(id_label, function(key, value) {
            if($("#chkbox_demog_" + key).is(':checked')) {
                // $("#demog_value_" + value).show();
                var result = "";
                
                result += "<div class=\"form-group\">";
                result += "    <label for=\"" + key + "\">" + value + "</label>";
                result += "    <input type=\"" + (key == "dob" ? "date": "text") + "\" class=\"form-control\" id=\"demog_" + key + "\" placeholder=\"Enter " + value + "\">";
                result += "</div>";
                $("#demog-result-" + (demog_result_id % 4 == 0 ? "4" : demog_result_id % 4)).append(result);
                demog_result_id += 1;
            }
            else {
                $("#demog_" + key).hide();
            }
        });

        $("#model-demog-inputs").modal('toggle');
    });

    function setActiveCategory(selectedCategoryId) {
        var categories = document.querySelectorAll('.list-group-item');
        categories.forEach(function (category) {
            category.classList.remove('active');
        });
        document.getElementById(selectedCategoryId).classList.add('active');
    }

    // Token Value

    $("#auth-type-fp").change(function() {
        disableFingerPrintForm(!$(this).prop("checked"));
    });

    $("#auth-type-iris").change(function() {
        disableIrisForm(!$(this).prop("checked"));
    });

    $("#auth-type-face").change(function() {
        disableFaceForm(!$(this).prop("checked"));
    });

    $("#auth-type-otp").change(function() {
        disableOTPForm(!$(this).prop("checked"));
    });

    $("#auth-type-demo").change(function() {
        disableDemographicForm(!$(this).prop("checked"));
    });

    $("#btn-model-demog-inputs").click(function() {
        $("#model-demog-inputs").modal('toggle');
    });

    $("#otp-request").click(function() {
        individual_id = $("#individual-id").val();
        individual_id_type = $("#individual-id-type").val();        
        otp_email = $("#otp-email").prop("checked");
        otp_phone = $("#otp-phone").prop("checked");

        $.ajax({
            type:"POST",
            url:"/request/otp/" + individual_id,
            data:{
                // _token: _token,
                individual_id: individual_id,
                individual_id_type: individual_id_type,
                otp_email: otp_email,
                otp_phone: otp_phone,
            },
            success:function(data) {
                var result = JSON.stringify(data, null, 4);
                $("#modal-result-value").text(result);
                $("#modal-result").modal("toggle");
            }
         });
    });

    $("#send-auth-request").click(function() {
        var demog_value = {};

        if($("#auth-type-demo").is(':checked')) {
            $.each(ids, function(key, value) {
                if($("#demog_" + value).val() != "" && $("#demog_" + value).val() != null) {
                    demog_value[key] = $("#demog_" + value).val();
                    if(key == "dob") {
                        demog_value[key] = new Date(demog_value[key]);
                        demog_value[key] = demog_value[key].getFullYear() + '/' + ('0' + (demog_value[key].getMonth() + 1)).slice(-2) + '/' + ('0' + demog_value[key].getDate()).slice(-2);;
                    }
                }
            });
        }
        
        demog_value = JSON.stringify(demog_value);

        var request_body = {
            "individual_id": $("#individual-id").val(),
            "individual_id_type": $("#individual-id-type").val(),
            
            "input_bio": $("#auth-type-bio").is(':checked') ? "on" : "off",
            "input_otp": $("#auth-type-otp").is(':checked') ? "on" : "off",
            "input_demo": $("#auth-type-demo").is(':checked') ? "on" : "off",
            "input_ekyc": $("#auth-type-ekyc").is(':checked') ? "on" : "off",
    
            "input_otp_value": $("#otp-value").val(),
            "input_demo_value": demog_value,
        }

        $.ajax({
            type:"POST",
            url: "/authenticate/",
            data: request_body,
            success: function(data) {
                var result = JSON.stringify(data, null, 4);
                $("#modal-result-value").text(result);
                $("#modal-result").modal("toggle");
            }
        });
    });
});

function disableFingerPrintForm(value) {
    $("#fingers-count").attr("disabled", value);
    $("#biometric-capture").attr("disabled", value);
}

function disableIrisForm(value) {
    $("#iris-type").attr("disabled", value);
    $("#biometric-capture").attr("disabled", value);
}

function disableFaceForm(value) {
    $("#biometric-capture").attr("disabled", value);
}

function disableOTPForm(value) {
    $("#otp-request").attr("disabled", value);
    $("#otp-value").attr("disabled", value);
    $("#otp-email").attr("disabled", value);
    $("#otp-phone").attr("disabled", value);
}

function disableDemographicForm(value) {
    $("#demographic-value").attr("disabled", value);
    $("#btn-model-demog-inputs").attr("disabled", value);
    $("input[id^=demog_]").attr("disabled", value);
}

function hideDemographicInputCategory() {
    $("div[id^=modal-demog-input-category-]").hide();
}