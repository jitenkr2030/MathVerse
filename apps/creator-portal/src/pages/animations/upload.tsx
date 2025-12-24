import { useState } from 'react';
import { useRouter } from 'next/router';
import { CreatorLayout } from '../../components/Layout';
import { useAuthStore } from '../../store';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Input, Select, Textarea } from '../../components/ui/Input';

const qualities = [
  { value: '720p', label: '720p (HD)' },
  { value: '1080p', label: '1080p (Full HD)' },
  { value: '1440p', label: '1440p (2K)' },
  { value: '4k', label: '4K (Ultra HD)' },
];

export default function UploadAnimationPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      console.log('File dropped:', e.dataTransfer.files[0]);
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <CreatorLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </CreatorLayout>
    );
  }

  return (
    <CreatorLayout title="Upload Animation - Creator Portal">
      <div className="p-6">
        <div className="max-w-3xl mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Upload Animation</h1>
            <p className="text-gray-600 mt-1">Create a new Manim animation for your lessons</p>
          </div>

          <Card className="mb-6">
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Animation Script</h2>
              
              <div className="space-y-6">
                <Input
                  label="Animation Title"
                  placeholder="e.g., Derivative Visualization"
                  required
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Input
                    label="Scene Class Name"
                    placeholder="e.g., DerivativeScene"
                    required
                    helperText="The Python class name that will be rendered"
                  />

                  <Input
                    label="Scene File Path"
                    placeholder="e.g., animations/calculus.py"
                    required
                    helperText="Path to the Python file containing the scene"
                  />
                </div>

                <Select
                  label="Quality"
                  options={qualities}
                  defaultValue="1080p"
                />

                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-600">
                    Drag and drop your Python script here, or click to select
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Supported formats: .py (Python script)</p>
                  <input type="file" className="hidden" accept=".py" />
                  <Button variant="outline" className="mt-4">Browse Files</Button>
                </div>

                <Textarea
                  label="Voiceover Script (Optional)"
                  placeholder="Enter the text for the voiceover narration..."
                  rows={4}
                  helperText="This text will be used to generate voiceover using text-to-speech"
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex items-center justify-end space-x-4">
            <Button variant="outline" onClick={() => router.back()}>Cancel</Button>
            <Button isLoading={isSubmitting}>Render Animation</Button>
          </div>
        </div>
      </div>
    </CreatorLayout>
  );
}
