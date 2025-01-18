//CPP
#include <iostream>
//ROOT
#include <TFile.h>
#include <TTree.h>
#include <TVector3.h>
#include <TH1D.h>
#include <TCanvas.h>
//JSAP
#include <JPSimOutput.hh>
//Self-Defined

int Check_Light_Source()
{
    std::string File_Path = "/home/penguin/Jinping/JSAP-install/Simulation/test.root";
    // Open the file
    TFile *file = new TFile(File_Path.c_str());
    TTree *sim_truth = (TTree*) file->Get("SimTruth");
    // sim_truth->Print();
    // Setup address
    Double_t pos_x, pos_y, pos_z;
    sim_truth->SetBranchAddress("x", &pos_x);
    sim_truth->SetBranchAddress("y", &pos_y);
    sim_truth->SetBranchAddress("z", &pos_z);
    std::vector<JPSimPrimaryParticle_t> *primary_particle_list = new std::vector<JPSimPrimaryParticle_t>;
    sim_truth->SetBranchAddress("PrimaryParticleList", &primary_particle_list);
    // Define variables in looping
    TVector3 Pos(1, 0, 0), Momentum(1, 0, 0);
    TVector3 Pos_Light(0, 0, 200);
    TH1D *hist = new TH1D("hist", "hist", 100, -1.0e-5, 1.0e-5);
    // Loop data
    for(int index = 0; index < sim_truth->GetEntries(); index++)
    {
        sim_truth->GetEntry(index);
        // Check Position of emitted photon
        // Pos.SetXYZ(pos_x, pos_y, pos_z);
        // Pos = Pos - Pos_Light;
        // hist->Fill(Pos.Mag());

        // Check Energy of emitted photon
        // hist->Fill(primary_particle_list->at(0).Ek);
        // hist->Fill(primary_particle_list->at(0).px);
        // hist->Fill(primary_particle_list->at(0).py);
        // hist->Fill(primary_particle_list->at(0).pz);
        // Momentum.SetXYZ(primary_particle_list->at(0).px, primary_particle_list->at(0).py, primary_particle_list->at(0).pz);
        // hist->Fill(Momentum.Mag());
        
    };
    // 输出
    TCanvas *canvas = new TCanvas("canvas", "canvas", 800, 600);
    hist->Draw();

    // delete hist;
    // delete canvas;
    return 0;
}