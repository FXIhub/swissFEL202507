#include <math.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SQR(A) ((A)*(A))
//#include <algorithm>
//#include "peakfinder8_my.h"
//#include "peakfinder9.cpp"
//#include "peakfinder8.cpp"
const int MASK_GOOD=1;
const int MASK_BAD=0;
const float MinVal=1e-10;
extern "C"{
float medianCutoff(float arr[], size_t n, float cutoff)  // cutoff from 0 to 1
{ if (n<1) return 0;
  const float maxval = 1e30;
  int upperlim = rint(cutoff*(n+0.01));
//  if (upperlim<1) upperlim=1;
  float _minim=arr[0];
  for (int jj=0; jj<upperlim; jj++)
  { _minim = maxval;
    int cmin = 0;
    for (int j=0; j<n; j++)
      if (arr[j]<_minim)
      { _minim = arr[j];
        cmin = j;
      }
    arr[cmin] = maxval;
  }
  return _minim;
}

    int SubLocalBG(float* inpAr, int stx, int enx, int sty, int eny, int fNumX, int radX, int radY, float badVal, float* smoothedAr)
{
  //float* inpAr = (float*)inpAr;
  float* arr1 = new float[(2*radX+1)*(2*radY+1)];
  int numX = enx-stx;
  int numY = eny-sty;
  size_t numComp = (size_t)numX*(size_t)numY;
  float* arrOld = new float[numComp];
  for (int xi=0; xi<numX; xi++)
    for (int yi=0; yi<numY; yi++)
      arrOld[xi+numX*yi] = inpAr[stx+xi+fNumX*(sty+yi)];

  if (smoothedAr != NULL)
    for (size_t i=0; i<numComp; i++)
      smoothedAr[i] = badVal;
//  for (size_t i=0; i<numComp; i++)
//    arrOld[i] = inpAr[i];

  for (int yi=0; yi<numY; yi++)
    for (int xi=0; xi<numX; xi++)
    { int nuel = 0;
      if (arrOld[xi+numX*yi]<badVal+1) continue;
      for (int bxi=-radX; bxi<=radX; bxi++)
        for (int byi=-radY; byi<=radY; byi++)
          if (xi+bxi>=0 && xi+bxi<numX && yi+byi>=0 && yi+byi<numY)
            if (arrOld[xi+bxi+numX*(yi+byi)]>badVal+1)
            { arr1[nuel] = arrOld[xi+bxi+numX*(yi+byi)];
              nuel++;
            }
      if (nuel>0)
      { //+float theval = quick_select(arr1, nuel);
        float theval = medianCutoff(arr1, nuel, 0.5);
        if (smoothedAr != NULL)
          smoothedAr[stx+xi+fNumX*(sty+yi)] = theval;
        else
          inpAr[stx+xi+fNumX*(sty+yi)] = arrOld[xi+numX*yi] - theval;
      }
    }

  delete arr1;
  delete arrOld;
  return 13;
}

void SubtractBgLoop(float* data, long pix_nn, int *pix_r, float hitfinderMinSNR, float ADCthresh, float bstpReg, float* radialcurve)
{
//! pix_r - array of radii of each pixel
//! hitfinderMinSNR - ?  it is =8 in cheetah.ini
//! ADCthresh -?  Some minimal threshold
  clock_t tStart = clock();
  const float MinVal = 1e-10;
  const int loopsNum = 5; // number of loops to make

  // Apply mask (multiply data by 0 to ignore regions - this makes data below threshold for peak finding)
//mask  for(long i=0;i<pix_nn;i++) temp[i] *= mask[i];

  // Determine noise and offset as a funciton of radius
  float fminr, fmaxr;
  long lminr, lmaxr;
  fminr = 1e9;
  fmaxr = -1e9;

  // Figure out radius bounds
  for(long i=0;i<pix_nn;i++){
    if (pix_r[i] > fmaxr)
      fmaxr = pix_r[i];
    if (pix_r[i] < fminr)
      fminr = pix_r[i];
  }
  lmaxr = (int)ceil(fmaxr)+1;
  lminr = 0;

  // Allocate and zero arrays
  float* rsigma = (float*) calloc (lmaxr, sizeof(float));
  float* roffset = (float*) calloc (lmaxr, sizeof(float));
  long* rcount = (long*) calloc (lmaxr, sizeof(long));
  float* lowthreshold = (float*) calloc (lmaxr, sizeof(float));
  float* rthreshold = (float*) calloc (lmaxr, sizeof(float));

  for(long i=0; i<lmaxr; i++)
  { rthreshold[i] = 1e9;
    lowthreshold[i] = -1e9;
  }

  // Compute sigma and average of data values at each radius
  // From this, compute the ADC threshold to be applied at each radius
  // Iterate a few times to reduce the effect of positive outliers (ie: peaks)
  for(long counter=0; counter<loopsNum; counter++) {
    for(long i=0; i<lmaxr; i++) {
      roffset[i] = 0;
      rsigma[i] = 0;
      rcount[i] = 0;
    }
    for(long i=0;i<pix_nn;i++){
//mask      if(mask[i] != 0)
      if (data[i]>bstpReg+1)
      { long thisr = pix_r[i];
        if(data[i] < rthreshold[thisr] && data[i] > lowthreshold[thisr]) {
          roffset[thisr] += data[i];
          rsigma[thisr] += (data[i]*data[i]);
          rcount[thisr] += 1;
        }
      }
    }
    for(long i=0; i<lmaxr; i++) {
      if(rcount[i] == 0) {
        roffset[i] = 0;
        rsigma[i] = 0;
        rthreshold[i] = 1e9;
        lowthreshold[i] = -1e9;
      }
      else {
        float thisoffset = roffset[i]/(float)rcount[i];        //!!!!! this is average. I need array for each i at last loop
        roffset[i] = thisoffset;
        float someval = rsigma[i]/(float)rcount[i] - thisoffset*thisoffset;
        if (someval>MinVal) rsigma[i] = sqrt(someval);
        else rsigma[i] = 0;
//        rsigma[i] = sqrt(rsigma[i]/rcount[i] - thisoffset*thisoffset);;
        rthreshold[i] = roffset[i] + hitfinderMinSNR*rsigma[i];
        lowthreshold[i] = roffset[i] - hitfinderMinSNR*rsigma[i];
        if(rthreshold[i] < ADCthresh) rthreshold[i] = ADCthresh;
         //rthreshold[i] = ADCthresh;  // For testing
      }
    }
  }

  FILE* afile = fopen("SubtractBgLoop.txt","w");
  for(long i=0; i<lmaxr; i++)
    fprintf(afile,"%0.2f\n",roffset[i]);
  fclose(afile);
  
  if (radialcurve != NULL){
    for(long i=0;i<lmaxr;i++)
      radialcurve[i] = roffset[i];}
  else{
    for(long i=0;i<pix_nn;i++)
      if (data[i]>bstpReg+1)
        data[i] -= roffset[pix_r[i]];
  }
  free (rsigma);
  free (roffset);
  free (rcount);
  free (rthreshold);
  free (lowthreshold);
  printf("Time of processing by Cheetah is taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
  return;
}

int roundCpp(double xd)
{ //double _xd = xd + 103079215104.5;
  //return ((int*)&_xd)[0] >> 16;
  double t = ((xd) + 6755399441055744.0);
  return *((int *)(&t));
}

int roundMy(float x)
{ double x1 = x;
  return roundCpp(x1);
  //  return (int)round(x);
};

bool BuildRadialArray(size_t numEl, float *cox, float* coy, float istep,
                  int* pix_r, int* maxRad, float* pixelsR)
{
  // determine number of components in radial array

  *maxRad = 0;
  for (size_t i=0; i<numEl; i++)
  { float distR = sqrt(SQR(cox[i])+SQR(coy[i]))*istep;
    if (pixelsR != NULL) pixelsR[i] = distR;
    size_t _ind = roundMy(distR);
    if (_ind > *maxRad) *maxRad = _ind;
  }
  *maxRad += 1;
  
  // forming the array
  for (int i=0; i<numEl; i++)
  { int _ind = roundMy(sqrt(SQR(cox[i])+SQR(coy[i]))*istep);
  //should never happen
    if (_ind>=*maxRad)
      {printf("In radial averaging components are too far!\n"); continue;}
    pix_r[i] = _ind;
    //printf("%d\n", pix_r[i]);
  }
  return true;
}

bool MedianFilter1D(float* inpAr, int numX, int radX, float badVal)
{
  float* arr1 = new float[(2*radX+1)];
  float* arrOld = new float[numX];
  for (int i=0; i<numX; i++)
    arrOld[i] = inpAr[i];

  for (int xi=0; xi<numX; xi++)
    { int nuel = 0;
      for (int bxi=-radX; bxi<=radX; bxi++)
          if (xi+bxi>=0 && xi+bxi<numX)
            if (arrOld[xi+bxi]>badVal+1)
            { arr1[nuel] = arrOld[xi+bxi];
              nuel++;
            }
      if (nuel>0)
        inpAr[xi] = medianCutoff(arr1, nuel, 0.5);
      else inpAr[xi] = badVal;
    }
  delete[] arr1;
  delete[] arrOld;
  return true;
}

float PolarisationFactorDet(float detx, float dety, float detz, float degree)
{ if ((fabs(detx)<MinVal && fabs(dety)<MinVal)) return 1.;
//  float phi = atan2(dety,detx);
//  float teta = atan2(sqrt(detx*detx+dety*dety),detz);
//  float pol = degree*(1.-SQR(sin(teta)*cos(phi))) + (1.-degree)*(1.-SQR(sin(teta)*sin(phi)));

  float pdist2i = 1/(detx*detx + dety*dety + detz*detz);
//+  float pol = degree*(1.-SQR(detx)*pdist2i) + (1.-degree)*(1.-SQR(dety)*pdist2i);
  float pol = 1 - (SQR(dety)*(1.-degree) + SQR(detx)*degree)*pdist2i;

//  float pol = degree*(1.-SQR(sin(teta)*cos(phi))) ;//+ (1.-degree)*(1.-SQR(cos(teta)*sin(phi)));
//CF  pol = 1. - 2.*(1 - SQR(sin(phi)*sin(teta))) + 1 + SQR(cos(teta));
//old  float pol = 1.-SQR(sin(teta)*cos(phi));
  if (fabs(pol)<MinVal) pol=1;
//  else pol = 1/pol;
  return pol;
}

void CorrectPolarisation(float* im, int numcomp, float* cox, float* coy, float detdist, float badReg, float poldegree)
{ if (fabs(detdist)>MinVal)
    for (int i=0; i<numcomp; i++)
      if (im[i]>badReg+1) im[i] /= PolarisationFactorDet(cox[i],coy[i],detdist,poldegree);
}

bool MakePolarisationArray(float* pol, int numcomp, float* cox, float* coy, float detdist, float poldegree)
{ //if (fabs(detdist)<MinVal || pol==NULL) return false;
  for (int i=0; i<numcomp; i++)
    pol[i] += PolarisationFactorDet(cox[i],coy[i],detdist,poldegree);
  return true;
}



int MaskRingsSimple(float* data, char *mask, int *pix_r, int numPo, float badVal, float ringDiff, int smF)
//int MaskRingsSimple(float* data, char *mask, int numPoRad, int** radShells, int* radialNumComp, float badVal, float ringDiff, int smF)
{
  // find max rad
  int numPoRad = 0;
  for (int pix=0; pix<numPo; pix++)
    if (pix_r[pix] > numPoRad)
      numPoRad = pix_r[pix];
  numPoRad++;

  int smoothF = smF;
  if (smoothF<MinVal) smoothF = numPoRad/30; //???
  float difference = ringDiff;//0.2;

  // make radial average curve
  float* radaver = new float[numPoRad];
  int* irad = new int[numPoRad];
  for (int ring=0; ring<numPoRad; ring++)
  { radaver[ring] = 0.;
    irad[ring] = 0;
  }

  //calculate radial averaged curve
  for (int pix=0; pix<numPo; pix++)
  { int ring = pix_r[pix];
    if (mask != NULL)
    { if (mask[pix]!=MASK_GOOD) continue;
    } //else
    if (data[pix]<badVal+1) continue;
    radaver[ring] += data[pix];
    irad[ring]++;
  }
  for (int ring=0; ring<numPoRad; ring++)
    if (irad[ring]>0) radaver[ring] /= (float)irad[ring];
    else radaver[ring] = badVal-1;

  // smooth it
  float* smradaver = new float[numPoRad];
  for (int ring=0; ring<numPoRad; ring++)
    smradaver[ring] = radaver[ring];
  printf("%f\t%f\t\n",smradaver[100],smradaver[200]);
  MedianFilter1D(smradaver, numPoRad, smoothF, badVal);
  printf("%f\t%f\t\n",smradaver[100],smradaver[200]);

  // mark bad rings in irad
  for (int ring=0; ring<numPoRad; ring++)
    if (irad[ring]>0)
      if (fabs(smradaver[ring])>MinVal)
        if (fabs((smradaver[ring]-radaver[ring])/smradaver[ring])>difference)
          irad[ring] = -1;

  // mask all rings where difference between original and smoothed is too big
  for (int pix=0; pix<numPo; pix++)
    if (irad[pix_r[pix]]<0)
      if (mask == NULL) 
        data[pix] = badVal;
      else mask[pix] = MASK_BAD;

  delete[] irad;
  delete[] radaver;
  delete[] smradaver;
}
}