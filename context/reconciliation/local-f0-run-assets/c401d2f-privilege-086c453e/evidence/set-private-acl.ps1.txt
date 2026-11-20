$ErrorActionPreference='Stop'
$privateTarget=[System.IO.Path]::GetFullPath($args[0])
$sid=[System.Security.Principal.WindowsIdentity]::GetCurrent().User
$acl=[System.Security.AccessControl.DirectorySecurity]::new()
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true,$false)
$rule=[System.Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
$acl.AddAccessRule($rule)
[System.IO.Directory]::SetAccessControl($privateTarget,$acl)
$actual=[System.IO.Directory]::GetAccessControl($privateTarget)
$rules=$actual.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 1 -or $rules[0].IdentityReference.Value -ne $sid.Value -or -not $actual.AreAccessRulesProtected -or $actual.GetOwner([System.Security.Principal.SecurityIdentifier]).Value -ne $sid.Value) { throw 'Owner-only ACL verification failed' }
Write-Output 'PRIVILEGE_ONLY_VERIFIED'
