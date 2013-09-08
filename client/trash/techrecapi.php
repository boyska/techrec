<?
include_once("function.php");

$op = $_GET['op'];

mymessage("<div>TechreAPI (ver ".VER."): OP=$op <div/>");

print "<br /> POST ";
print_r ($_POST);

print "<br /> GET ";
print_r($_GET);

switch ($op) {
    case "install":
        $db = connect();
        rec_install();
        disconnect($db);

        break; 
                
    case "new":
        $db = connect();
        rec_new( $db, $_POST );
        disconnect($db);

        break;
        
    case "del":
        $db = connect();
        rec_del( $db, $_GET['id'] );
        disconnect($db);

        break; 
        
    case "update":
        $db = connect();
        rec_update($db, $_POST );
        disconnect($db);
        break; 
        
    case "search":
        
        $db = connect();
        rec_get($db, $_GET );
        disconnect($db);
        
        break;

    case "help":
        help();

        break;
        
    default:
        exit( -1 );
}
?>
