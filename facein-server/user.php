<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');
session_start();
include("config.php");
include("header.php");

if(isset($_SESSION["username"])){
	$username = $_SESSION["username"];
	$statement = $connection->prepare("SELECT * FROM `users` WHERE `username` = ?");
	$statement->bind_param("s", $username);
	$statement->execute();
	$result = $statement->get_result();
	$row = $result->fetch_assoc();
	$id = $row["id"];
	$password = $row["password"];
	
	
} else {
	header("Location: index.php");
	exit();
}


?>



<div class="mt-4 mt-10p" id="qr"></div>

<p class="instruction mt-4" style="text-align: center;">QR Code successfully generated</p>

<div class="instruction mt-2" style="text-align: center;">Right click or Hold press to download</div>

<div class="logout mt-4">
	<a href="index.php?logout">
		<button class="logout-button">
			<i class="fas fa-sign-out-alt"></i>
			Logout
		</button>
	</a>
</div>

<script language="javascript">
var qrcode = new QRCode("qr");
var password = "<?php echo $password; ?>";
qrcode.makeCode(password);
</script>


<?php include("footer.php") ?>