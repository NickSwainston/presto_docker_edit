#!/usr/bin/env python3

from builtins import map
import re, glob, argparse
import presto.sifting as sifting
from operator import itemgetter, attrgetter

parser = argparse.ArgumentParser(description="""
Finds candidates with DM paterns.
""")
parser.add_argument('--dir', type=str, default="./",
                    help="Work dir. Should be my search sub dirs, eg DM_000-002.")
parser.add_argument('-f', '--file_name', type=str, default="",
                    help="The filename to be used for the output file cand_<file_name>.txt")

parser.add_argument('--min_num_DMs', type=int, default=8,
                    help='In how many DMs must a candidate be detected to be considered "good"')
parser.add_argument('--low_DM_cutoff', type=float, default=1.0,
                    help='Lowest DM to consider as a "real" pulsar')
parser.add_argument('--sigma_threshold', type=float, default=3.0,
                    help='Ignore candidates with a sigma (from incoherent power summation) less than this')
parser.add_argument('--c_pow_threshold', type=float, default=10.0,
                    help='Ignore candidates with a coherent power less than this')

parser.add_argument('--known_birds_p', type=float, nargs='*', default=[],
                    help="If the birds file works well, the following shouldn't be needed at all..."
                         "If they are, add tuples with the bad values and their errors. (ms, err)")
parser.add_argument('--known_birds_f', type=float, nargs='*', default=[],
                    help="If the birds file works well, the following shouldn't be needed at all..."
                         "If they are, add tuples with the bad values and their errors. (Hz, err)")

parser.add_argument('--r_err', type=float, default=1.1,
                    help='How close a candidate has to be to another candidate to '
                          'consider it the same candidate (in Fourier bins)')
parser.add_argument('--short_period', type=float, default=0.0005,
                    help='Shortest period candidates to consider (s)')
parser.add_argument('--long_period', type=float, default=15.0,
                    help='Longest period candidates to consider (s)')
parser.add_argument('--harm_pow_cutoff', type=float, default=3.0,
                    help='Ignore any candidates where at least one harmonic does exceed this power')
args=parser.parse_args()

d=args.dir
if d.endswith("/"):
    d = d[:-1]
# glob for ACCEL files
globaccel = "{0}/*ACCEL_*0".format(d)
# glob for .inf files
globinf = "{0}/*DM*.inf".format(d)
inffiles = glob.glob(globinf)
candfiles = glob.glob(globaccel)

sifting.sigma_threshold = args.sigma_threshold
sifting.c_pow_threshold = args.c_pow_threshold
sifting.known_birds_p = args.known_birds_p
sifting.known_birds_f = args.known_birds_f

# The following are all defined in the sifting module.
# But if we want to override them, uncomment and do it here.
# You shouldn't need to adjust them for most searches, though.
sifting.r_err = args.r_err
sifting.short_period = args.short_period
sifting.long_period = args.long_period
sifting.harm_pow_cutoff = args.harm_pow_cutoff

#--------------------------------------------------------------

# Try to read the .inf files first, as _if_ they are present, all of
# them should be there.  (if no candidates are found by accelsearch
# we get no ACCEL files...

# Check to see if this is from a short search
if len(re.findall("_[0-9][0-9][0-9]M_" , inffiles[0])):
    dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
else:
    dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
dms = list(map(float, dmstrs))
dms.sort()
dmstrs = ["%.2f"%x for x in dms]

# Read in all the candidates
cands = sifting.read_candidates(candfiles)

# Remove candidates that are duplicated in other ACCEL files
if len(cands):
    cands = sifting.remove_duplicate_candidates(cands)

# Remove candidates with DM problems
if len(cands) and args.min_num_DMs > 1:
    cands = sifting.remove_DM_problems(cands, args.min_num_DMs, dmstrs, args.low_DM_cutoff)

# Remove candidates that are harmonically related to each other
# Note:  this includes only a small set of harmonics
if len(cands) > 1:
    cands = sifting.remove_harmonics(cands)
print("Number of candidates remaining {}".format(len(cands)))
# Write candidates to STDOUT
if args.file_name:
    cands_file_name = 'cands_{}.txt'.format(args.file_name)
elif args.dir == "./":
    cands_file_name = 'cands.txt'
else:
    cands_file_name = 'cand_files/cands_'+ d.replace("/","_") +'.txt'

if len(cands):
    cands.sort(key=attrgetter('sigma'), reverse=True)
    sifting.write_candlist(cands, candfilenm=cands_file_name)
    print(cands_file_name)
else:
    print("No candidates left, created no file")
