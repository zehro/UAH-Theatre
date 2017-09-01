// Constants
var animationDuration = 300;

// Launches initialize() function on document load
initialize();

function initialize()
{
    // Loads the login template
    loadTemplate( 'pages/index/index_login_template.html' );
}

function loadTemplate( template, username='', password='' )
{
    // Loads the template
    $( '#main_content' ).load( template, function()
    {
        // Loads in any input values from the passed in arguments
        $( '#username' ).val( username );
        $( '#password' ).val( password );

        // Triggers the 'Fade In' animation after template loads
        $( '#main_content' ).removeClass().addClass( 'fade_in' );

        // Clears the animation classes after the animation duration
        setTimeout( function()
        {
            $( '#main_content' ).removeClass();
        }, animationDuration );
    });
}

function loadLogin()
{
    // Triggers the 'Fade Out' animation
    $( '#main_content' ).addClass( 'fade_out' );

    // Loads the Login template after the animation duration
    setTimeout( function()
    {
        loadTemplate( 'pages/index/index_login_template.html' );
    }, animationDuration );
}

function loadRegister()
{
    // Triggers the 'Fade Out' animation
    $( '#main_content' ).addClass( 'fade_out' );

    // Loads the Register template after the animation duration
    setTimeout( function()
    {
        // Loads values from input fields if there's any
        loadTemplate(
            'pages/index/index_register_template.html',
            $( '#username' ).val(),
            $( '#password' ).val()
        );
    }, animationDuration );
}

function clearErrorMessages()
{
    $( '.error_text' ).text( '' );
}
