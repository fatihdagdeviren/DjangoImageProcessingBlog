/**
 * Created by fatih on 11.11.2017.
 */
 function inputKontrol() {
        var file = document.getElementById('input-b1');
        var ext = file.value.match(/\.([^\.]+)$/)[1];
        switch (ext.toLowerCase()) {
            case 'jpg':
            case 'jpeg':
            case 'png':
                break;
            default:
                alert('This extension is not allowed (Only .jpg,.jpeg and .png files are allowed)');
                file.value = "";
                this.value = '';
        }
    };
