#include "lcms2.h"
int main(void)
{
	cmsViewingConditions vc, vc2;
	cmsCIEXYZ In;
	cmsJCh Out;
	cmsHANDLE h1, h2;

	vc.whitePoint.X = 98.88;
	vc.whitePoint.Y = 90.00;
	vc.Yb = 18;
	vc.La = 200;
	vc.surround = AVG_SURROUND;
	vc.D_value  = 1.0;

	h1 = cmsCIECAM02Init(0, &vc);

	vc2.whitePoint.X = 98.88;
	vc2.whitePoint.Y = 100.00;
	vc2.whitePoint.Z = 32.03;

	vc2.Yb = 20;
	vc2.La = 20;
	vc2.surround = AVG_SURROUND;
	vc2.D_value  = 1.0;
	h2 = cmsCIECAM02Init(0, &vc);

	In.X= 19.31;
	In.Y= 23.93;
	In.Z =10.14;

	cmsCIECAM02Forward(h1, &In, &Out);
	cmsCIECAM02Reverse(h2, &Out, &In);

	cmsCIECAM02Done(h1);
	cmsCIECAM02Done(h2);
	return 0;
}