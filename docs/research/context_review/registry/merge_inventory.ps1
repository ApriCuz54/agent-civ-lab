param([string]$Root = $PSScriptRoot)
# Provenance-preserving inventory; does not certify unique studies or claim verification.
$reviewRoot = Split-Path $Root -Parent
$sourceRows = @(); $claimRows = @(); $searchRows = @()
function FirstField($row, $fields) { foreach ($field in $fields) { if ($row.$field) { return $row.$field } }; return 'unknown' }
foreach ($laneDir in (Get-ChildItem (Join-Path $reviewRoot 'workstreams') -Directory | Sort-Object Name)) {
  $laneName = $laneDir.Name
  $sourceFile = Join-Path $laneDir.FullName 'sources.csv'
  if (Test-Path $sourceFile) { foreach ($row in (Import-Csv $sourceFile)) {
    $url = FirstField $row @('primary_url','url'); $identity = $url
    if ($url -match 'arxiv.org/(abs|pdf|html)/(\d{4}\.\d{4,5})') { $identity = 'arxiv:' + $Matches[2] }
    $localId = FirstField $row @('source_id','id')
    $sourceRows += [pscustomobject]@{registry_id=($laneName+':'+$localId); canonical_candidate=$identity; title=$row.title; primary_url=$url; reading_status=(FirstField $row @('reading_status','evidence_status','review_depth','access_status','access_and_reading','access')); independent_verification='pending'; record_json=($row|ConvertTo-Json -Compress)}
  }}
  foreach ($kind in @('claims','search_log')) {
    $tableFile = Join-Path $laneDir.FullName ($kind+'.csv')
    if (Test-Path $tableFile) { $rowIndex=0; foreach ($row in (Import-Csv $tableFile)) { $rowIndex++; $entry=[pscustomobject]@{registry_id=($laneName+':'+$kind+':'+$rowIndex); stream=$laneName; independent_verification='pending'; record_json=($row|ConvertTo-Json -Compress)}; if ($kind -eq 'claims') {$claimRows += $entry} else {$searchRows += $entry} } }
  }
}
$sourceRows|Export-Csv (Join-Path $Root 'sources.csv') -NoTypeInformation -Encoding utf8
$claimRows|Export-Csv (Join-Path $Root 'claims.csv') -NoTypeInformation -Encoding utf8
$searchRows|Export-Csv (Join-Path $Root 'search_log.csv') -NoTypeInformation -Encoding utf8
[pscustomobject]@{source_records=$sourceRows.Count;candidate_identity_groups=(@($sourceRows.canonical_candidate|Sort-Object -Unique)).Count;claim_records=$claimRows.Count;search_records=$searchRows.Count}|ConvertTo-Json
