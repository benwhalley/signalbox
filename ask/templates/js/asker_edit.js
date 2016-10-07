ZeroClipboard.setDefaults({
    trustedOrigins: [window.location.protocol + "//" + window.location.host]
});
ZeroClipboard.setDefaults({
    moviePath: '{{STATIC_URL}}js/ZeroClipboard.swf'
});
var clip = new ZeroClipboard($(".copy-button"));
clip.on('complete', function(client, args) {
    $.notify({
        // options
        message: "Copied text to clipboard: " + args.text
    }, {
        // settings
        type: 'info',
        delay: 500
    });
});
