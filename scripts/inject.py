import argparse
import atpy
import sim

parser = argparse.ArgumentParser(
    description='Inject transit into template light curve.')

parser.add_argument('inp',  type=str   , help='input file')
parser.add_argument('out',  type=str   , help='output file')
parser.add_argument('P',    type=float , help='Period (days)')
parser.add_argument('epoch',type=float , help='Epoch (days)')
parser.add_argument('df',   type=float , help='Depth (ppm)')
parser.add_argument('tdur', type=float , help='Transit Duration (days)')

args = parser.parse_args()

tinp = atpy.TableSet(args.inp,type='fits')
d = dict(P=args.P,epoch=args.epoch,tdur=args.tdur,df=args.df)

func = lambda t : sim.tinject(t,d)
tout = map(func,tinp)
tout = atpy.TableSet(tout)

tout.write(args.out,overwrite=True,type='fits')
print "inject: Created %s" % args.out