Try
{
	# To wipe out previous results
	$Results = $null

	$Results = Invoke-SqlCmd -query `
	"SELECT 'Edition', SERVERPROPERTY('Edition'); 
	 SELECT 'Product Version', SERVERPROPERTY('ProductVersion');
	 SELECT 'Product Level', SERVERPROPERTY('ProductLevel');" `
	-ServerInstance "localhost" | Select-Object -Property Column1, @{label = 'Result'; expression = { $_.Column2}} `
								| Select-Object -Property Result, @{label = 'Query'; expression = { $_.Column1}}
	
	# query properly executed
	$SQLQuerySuccess = $TRUE

}
Catch
{
	# query did not properly execute :(
	# SQL probably doesn't exist on this server, or you have inadequate access rights, etc
	$SQLQuerySuccess = $FALSE
}

# output of results
"Did SQL Query Run? : $SQLQuerySuccess"
"Result of Query:" 
$Results 
