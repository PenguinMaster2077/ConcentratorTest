//CPP
#include <iostream>
#include <fstream>
//ROOT
#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TStyle.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined
#include "./Heads/Count_Photon.hh"
#include "./Heads/Parallel_Photon.hh"

// void Parallel_Photon()
// {
//     std::string Pic_Dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/test";
//     Int_t PMT = 2;
//     Int_t Wavelength = 415;
//     std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test_100k_60.root";
//     std::string Strings = "60";
//     Double_t Number_Photon = Count_Parallel_Photon(PMT, File_Path, Pic_Dir, Strings, Wavelength);
// }

void Parallel_Photon(Int_t Wavelength)
{
    std::cout << "[Parallel_Photon] Start Processing " << Wavelength << std::endl;
    // PMT
    Count_Parallel_Photon(Wavelength, 0);
    // Concentrator
    // Count_Parallel_Photon(Wavelength, 1);
    std::cout << "[Parallel_Photon] Complete!" << std::endl;
    
}