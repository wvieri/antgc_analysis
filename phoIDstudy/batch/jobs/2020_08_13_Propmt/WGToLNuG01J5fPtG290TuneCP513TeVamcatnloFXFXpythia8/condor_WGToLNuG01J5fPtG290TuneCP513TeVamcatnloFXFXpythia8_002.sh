executable				= /data/cmszfs1/user/wadud/aNTGCmet/aNTGC_analysis/phoIDstudy/batch/jobs/2020_08_13_Propmt//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8_002.sh
output                	= /data/cmszfs1/user/wadud/aNTGCmet/aNTGC_analysis/phoIDstudy/batch/jobs/2020_08_13_Propmt//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8//log//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8_002.out
error                 	= /data/cmszfs1/user/wadud/aNTGCmet/aNTGC_analysis/phoIDstudy/batch/jobs/2020_08_13_Propmt//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8//log//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8_002.err
log                   	= /data/cmszfs1/user/wadud/aNTGCmet/aNTGC_analysis/phoIDstudy/batch/jobs/2020_08_13_Propmt//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8//log//WGToLNuG01J5fPtG290TuneCP513TeVamcatnloFXFXpythia8_002.log
should_transfer_files   = Yes
when_to_transfer_output = ON_EXIT
request_memory			= 2000M
request_disk			= 1000M
Requirements 			=  (Machine != "scorpion10.spa.umn.edu") && (Machine != "scorpion6.spa.umn.edu") &&(Machine != "scorpion1.spa.umn.edu") && (Machine != "spa-sl7test.spa.umn.edu") && (Machine != "zebra01.spa.umn.edu") && (Machine != "zebra02.spa.umn.edu")  && (Machine != "zebra03.spa.umn.edu")  && (Machine != "zebra04.spa.umn.edu") && (Machine != "scorpion3.spa.umn.edu") && (Machine != "scorpion4.spa.umn.edu") && (Machine != "scorpion5.spa.umn.edu")
#next_job_start_delay	= 3
+JobFlavour 			= "workday"
queue